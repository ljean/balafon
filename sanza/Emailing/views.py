# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from sanza.Crm.models import Contact, Action, ActionType
from datetime import date, timedelta, datetime
from sanza.Emailing import models, forms
from django.contrib import messages
from colorbox.decorators import popup_redirect
from coop_cms.models import Newsletter
from sanza.Emailing.utils import get_emailing_context, get_credit
from django.template.loader import get_template
from django.conf import settings
from django.utils.importlib import import_module
from sanza.permissions import can_access
from utils import send_verification_email
from sanza.utils import logger, log_error
from sanza.utils import now_rounded

@user_passes_test(can_access)
def newsletter_list(request):
    newsletters = Newsletter.objects.all().order_by('-id')
    
    credits = sum([c.credit for c in models.EmailingCounter.objects.filter(credit__gt=0)])
    
    return render_to_response(
        'Emailing/newsletter_list.html',
        {'newsletters': newsletters, 'credits': credits},
        context_instance=RequestContext(request)
    )

@user_passes_test(can_access)
@popup_redirect
def delete_emailing(request, emailing_id):
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            emailing.delete()
        return HttpResponseRedirect(reverse('emailing_newsletter_list'))

    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'message': _(u"Are you sure to delete '{0.newsletter.subject}' {1}?").format(
                emailing, emailing.get_status_display()),
            'action_url': reverse("emailing_delete", args=[emailing_id]),
        },
        context_instance=RequestContext(request)
    )

@user_passes_test(can_access)
def view_emailing(request, emailing_id):
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    return render_to_response(
        'Emailing/view_emailing.html',
        {'emailing': emailing, 'contacts': emailing.get_contacts()},
        context_instance=RequestContext(request)
    )

@user_passes_test(can_access)
@popup_redirect
def new_newsletter(request):
    try:
        if request.method == 'POST':
            form = forms.NewNewsletterForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data["subject"]
                template = form.cleaned_data["template"]
                content = form.cleaned_data["content"]
                source_url = form.cleaned_data["source_url"]
                go_to_edit = False
                if not content:
                    content = _(u"Enter the text of your newsletter here")
                    go_to_edit = True
                
                newsletter = Newsletter.objects.create(
                    subject=subject, template=template, content=content, source_url=source_url
                )
                
                if go_to_edit:
                    return HttpResponseRedirect(newsletter.get_edit_url())
                else:
                    return HttpResponseRedirect(newsletter.get_absolute_url())
        else:
            form = forms.NewNewsletterForm()
    
        return render_to_response(
            'Emailing/new_newsletter.html',
            {'form': form},
            context_instance=RequestContext(request)
        )
    except Exception, msg:
        print "#ERR", msg
        raise

@user_passes_test(can_access)
@popup_redirect
def confirm_send_mail(request, emailing_id):
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    if request.method == "POST":
        if 'confirm' in request.POST:
            if emailing.status == models.Emailing.STATUS_EDITING:
                emailing.status = models.Emailing.STATUS_SCHEDULED
                emailing.scheduling_dt = now_rounded() + timedelta(minutes=1)
                emailing.save()
                messages.add_message(request, messages.SUCCESS, _(u"The sending has been scheduled"))
            else:
                messages.add_message(request, messages.ERROR, _(u"The sending can't be scheduled"))
            return HttpResponseRedirect(reverse('emailing_newsletter_list'))
    
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'message': _(u'Is this newsletter ready to be sent?'),
            'action_url': reverse("emailing_confirm_send_mail", args=[emailing_id]),
        },
        context_instance=RequestContext(request)
    )

@user_passes_test(can_access)
@popup_redirect
def cancel_send_mail(request, emailing_id):
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    if request.method == "POST":
        if 'confirm' in request.POST:
            if emailing.status in (models.Emailing.STATUS_SCHEDULED, models.Emailing.STATUS_CREDIT_MISSING):
                emailing.status = models.Emailing.STATUS_EDITING
                emailing.scheduling_dt = None
                emailing.save()
                messages.add_message(request, messages.SUCCESS, _(u"The sending has been cancelled"))
            else:
                messages.add_message(request, messages.ERROR, _(u"The sending can't be cancelled"))
            return HttpResponseRedirect(reverse('emailing_newsletter_list'))
    
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'message': _(u'Cancel the sending?'),
            'action_url': reverse("emailing_cancel_send_mail", args=[emailing_id]),
        },
        context_instance=RequestContext(request)
    )

def view_link(request, link_uuid, contact_uuid):
    link = get_object_or_404(models.MagicLink, uuid=link_uuid)
    try:
        contact = Contact.objects.get(uuid=contact_uuid)
        link.visitors.add(contact)
        
        #create action
        link_action, _is_new = ActionType.objects.get_or_create(name=_(u'Link'))
        action = Action.objects.create(
            entity = contact.entity, subject=link.url, planned_date=now_rounded(),
            type=link_action, detail='', contact=contact, done=True, display_on_board=False,
            done_date=now_rounded()
        )
        
    except Contact.DoesNotExist:
        pass
    return HttpResponseRedirect(link.url)
            
def unregister_contact(request, emailing_id, contact_uuid):
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    try:
        emailing = models.Emailing.objects.get(id=emailing_id)
    except models.Emailing.DoesNotExist:
        emailing = None
    my_company = settings.SANZA_MY_COMPANY
    
    if request.method == "POST":
        if 'unregister' in request.POST:
            form = forms.UnregisterForm(request.POST)
            if form.is_valid():
                contact.accept_newsletter = False
                contact.save()
                
                #create action
                entity = contact.entity
                
                emailing_action, _is_new = ActionType.objects.get_or_create(name=_(u'Unregister'))
                action = Action.objects.create(
                    entity=entity , subject=_(u'{0} has unregister').format(contact),
                    planned_date=now_rounded(), type = emailing_action, detail=form.cleaned_data['reason'],
                    contact=contact, done=True, display_on_board=False, done_date=now_rounded()
                )
                unregister = True
                return render_to_response(
                    'Emailing/public/unregister_done.html',
                    locals(),
                    context_instance=RequestContext(request)
                )
            else:
                pass #not valid : display with errors
        
        else:
            return render_to_response(
                'Emailing/public/unregister_done.html',
                locals(),
                context_instance=RequestContext(request)
            )
    else:
        form = forms.UnregisterForm()

    return render_to_response(
        'Emailing/public/unregister_confirm.html',
        locals(),
        context_instance=RequestContext(request)
    )

def view_emailing_online(request, emailing_id, contact_uuid):
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    context = Context(get_emailing_context(emailing, contact))
    t = get_template(emailing.newsletter.get_template_name())
    return HttpResponse(t.render(context))

def subscribe_newsletter(request):
    try:
        form_name = getattr(settings, 'SANZA_SUBSCRIBE_FORM')
        module_name, class_name = form_name.rsplit('.', 1)
        module = import_module(module_name)
        SubscribeForm = getattr(module, class_name)
    except AttributeError:
        SubscribeForm = forms.SubscribeForm
    
    if request.method == "POST":
        form = SubscribeForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(request)
            try:
                send_verification_email(contact)
                return HttpResponseRedirect(reverse('emailing_subscribe_done', args=[contact.uuid]))
            except:
                logger.exception('send_verification_email')
                
                #create action
                detail = _(u"An error occured while verifying the email address of this contact.")
                fix_action, _is_new = ActionType.objects.get_or_create(name=_(u'Sanza'))
                action = Action.objects.create(
                    subject=_(u"Need to verify the email address"), planned_date=now_rounded(),
                    type = fix_action, detail=detail, contact=contact, display_on_board=True,
                )
                
                return HttpResponseRedirect(reverse('emailing_subscribe_error', args=[contact.uuid]))
    else:
        form = SubscribeForm()
        
    context_dict = {
        'form': form,
    }
        
    return render_to_response(
        'Emailing/public/subscribe.html',
        context_dict,
        context_instance=RequestContext(request)
    )

def subscribe_done(request, contact_uuid):
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    my_company = settings.SANZA_MY_COMPANY
    
    return render_to_response(
        'Emailing/public/subscribe_done.html',
        locals(),
        context_instance=RequestContext(request)
    )
    
def subscribe_error(request, contact_uuid):
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    my_company = settings.SANZA_MY_COMPANY
    
    return render_to_response(
        'Emailing/public/subscribe_error.html',
        locals(),
        context_instance=RequestContext(request)
    )

def email_verification(request, contact_uuid):
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    my_company = settings.SANZA_MY_COMPANY
    
    contact.email_verified = True
    contact.save()
    
    return render_to_response(
        'Emailing/public/verification_done.html',
        locals(),
        context_instance=RequestContext(request)
    )
