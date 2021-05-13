# -*- coding: utf-8 -*-
"""emailing views"""

import datetime
import os.path

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView

from colorbox.decorators import popup_redirect
from coop_cms.models import Newsletter
from coop_cms.utils import redirect_to_language, paginate
from wsgiref.util import FileWrapper

from balafon.permissions import can_access
from balafon.utils import logger
from balafon.utils import now_rounded
from balafon.Crm.forms import ConfirmForm
from balafon.Crm.models import Contact, Action, ActionType, Subscription
from balafon.Crm.signals import new_subscription
from balafon.Emailing import models, forms
from balafon.Emailing.settings import (
    is_subscribe_enabled, is_email_subscribe_enabled, get_subscription_form, notify_subscription_on_confirmation
)
from balafon.Emailing.utils import (
    get_emailing_context, send_verification_email, EmailSendError, patch_emailing_html, send_notification_email
)


@user_passes_test(can_access)
def newsletter_list(request):
    """display list of newsletters"""
    newsletters = Newsletter.objects.all().order_by('-id')
    page_obj = paginate(request, newsletters, 10)
    return render(
        request,
        'Emailing/newsletter_list.html',
        {
            'newsletters': list(page_obj),
            'page_obj': page_obj
        }
    )


@user_passes_test(can_access)
@popup_redirect
def delete_emailing(request, emailing_id):
    """delete an emailing"""

    emailing = get_object_or_404(models.Emailing, id=emailing_id)

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                emailing.delete()
            return HttpResponseRedirect(reverse('emailing_newsletter_list'))
    else:
        form = ConfirmForm()

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _("Are you sure to delete '{0.newsletter.subject}' {1}?").format(
                emailing, emailing.get_status_display()),
            'action_url': reverse("emailing_delete", args=[emailing_id]),
        }
    )


@user_passes_test(can_access)
def view_emailing(request, emailing_id):
    """view an emailing"""

    emailing = get_object_or_404(models.Emailing, id=emailing_id)

    return render(
        request,
        'Emailing/view_emailing.html',
        {'emailing': emailing, 'contacts': emailing.get_contacts()}
    )


@user_passes_test(can_access)
@popup_redirect
def new_newsletter(request):
    """create a new newsletter"""
    try:
        if request.method == 'POST':
            form = forms.NewNewsletterForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data["subject"]
                template = form.cleaned_data["template"]
                content = form.cleaned_data["content"]
                source_url = form.cleaned_data["source_url"]
                site = form.cleaned_data["site"]
                go_to_edit = False
                if not content:
                    content = _("Enter the text of your newsletter here")
                    go_to_edit = True

                newsletter = Newsletter.objects.create(
                    subject=subject,
                    template=template,
                    content=content,
                    source_url=source_url,
                    site=site
                )

                if go_to_edit:
                    return HttpResponseRedirect(newsletter.get_edit_url())
                else:
                    return HttpResponseRedirect(newsletter.get_absolute_url())
        else:
            form = forms.NewNewsletterForm()

        return render(
            request,
            'Emailing/new_newsletter.html',
            {'form': form}
        )
    except Exception as msg:
        print("#ERR", msg)
        raise


@user_passes_test(can_access)
@popup_redirect
def confirm_send_mail(request, emailing_id):
    """schedule a emailing sending"""
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    if request.method == "POST":
        form = forms.NewsletterSchedulingForm(request.POST, instance=emailing)
        if form.is_valid() and ("confirm" in request.POST):
            if emailing.status == models.Emailing.STATUS_EDITING:
                emailing = form.save()
                emailing.status = models.Emailing.STATUS_SCHEDULED
                emailing.save()
                messages.add_message(request, messages.SUCCESS, _("The sending has been scheduled"))
            else:
                messages.add_message(request, messages.ERROR, _("The sending can't be scheduled"))
            return HttpResponseRedirect(reverse('emailing_newsletter_list'))
    else:
        form = forms.NewsletterSchedulingForm(instance=emailing)

    return render(
        request,
        'Emailing/confirm_send_mail.html',
        {
            'form': form,
            'message': _('Is this newsletter ready to be sent?'),
            'action_url': reverse("emailing_confirm_send_mail", args=[emailing_id]),
        }
    )


@user_passes_test(can_access)
@popup_redirect
def cancel_send_mail(request, emailing_id):
    """cancel an emailing sending"""

    emailing = get_object_or_404(models.Emailing, id=emailing_id)

    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if emailing.status in (models.Emailing.STATUS_SCHEDULED, ):
                    emailing.status = models.Emailing.STATUS_EDITING
                    emailing.scheduling_dt = None
                    emailing.save()
                    messages.add_message(request, messages.SUCCESS, _("The sending has been cancelled"))
                else:
                    messages.add_message(request, messages.ERROR, _("The sending can't be cancelled"))
            return HttpResponseRedirect(reverse('emailing_newsletter_list'))
    else:
        form = ConfirmForm()

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _('Cancel the sending?'),
            'action_url': reverse("emailing_cancel_send_mail", args=[emailing_id]),
        }
    )


def view_link(request, link_uuid, contact_uuid):
    """view magic link"""
    link = get_object_or_404(models.MagicLink, uuid=link_uuid)

    try:
        contact = Contact.objects.get(uuid=contact_uuid)
        link.visitors.add(contact)

        # create action
        link_action = ActionType.objects.get_or_create(name=_('Link'))[0]
        action = Action.objects.create(
            subject=link.url[:200], planned_date=now_rounded(),
            type=link_action, detail='', done=True, display_on_board=False,
            done_date=now_rounded()
        )
        action.contacts.add(contact)
        action.save()

    except Contact.DoesNotExist:
        pass

    return HttpResponseRedirect(link.url)


def unregister_contact(request, emailing_id, contact_uuid):
    """contact unregistrer from emailing list"""

    contact = get_object_or_404(Contact, uuid=contact_uuid)
    try:
        emailing = models.Emailing.objects.get(id=emailing_id)
        my_company = emailing.subscription_type.name
    except models.Emailing.DoesNotExist:
        emailing = None
        my_company = getattr(settings, 'BALAFON_MY_COMPANY', '')

    if request.method == "POST":
        if 'unregister' in request.POST:
            form = forms.UnregisterForm(request.POST)
            if form.is_valid():
                if emailing and emailing.subscription_type:
                    subscription = Subscription.objects.get_or_create(
                        contact=contact, subscription_type=emailing.subscription_type
                    )[0]
                    subscription.accept_subscription = False
                    subscription.unsubscription_date = datetime.datetime.now()
                    subscription.save()

                    emailing_action = ActionType.objects.get_or_create(name=_('Unregister'))[0]
                    action = Action.objects.create(
                        subject=_('{0} has unregister').format(contact),
                        planned_date=now_rounded(), type=emailing_action, detail=form.cleaned_data['reason'],
                        done=True, display_on_board=False, done_date=now_rounded()
                    )
                    action.contacts.add(contact)
                    action.save()

                    emailing.unsub.add(contact)
                    emailing.save()

                return render(
                    request,
                    'Emailing/public/unregister_done.html',
                    {
                        'contact': contact,
                        'emailing': emailing,
                        'form': form,
                        'my_company': my_company,
                        'unregister': True,
                    }
                )
            else:
                pass  # not valid : display with errors

        else:
            return render(
                request,
                'Emailing/public/unregister_done.html',
                {
                    'contact': contact,
                    'emailing': emailing,
                    'my_company': my_company
                }
            )
    else:
        form = forms.UnregisterForm()

    return render(
        request,
        'Emailing/public/unregister_confirm.html',
        {
            'contact': contact,
            'emailing': emailing,
            'form': form,
            'my_company': my_company
        }
    )


def view_emailing_online(request, emailing_id, contact_uuid):
    """view an emailing online"""
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    context = get_emailing_context(emailing, contact)
    the_template = get_template(emailing.newsletter.get_template_name())
    html_text = the_template.render(context)
    html_text = patch_emailing_html(html_text, emailing, contact)
    return HttpResponse(html_text)


def view_emailing_online_lang(request, emailing_id, contact_uuid, lang):
    """view an emailing in a given lang"""
    url = reverse("emailing_view_online", args=[emailing_id, contact_uuid])
    return redirect_to_language(url, lang)


def subscribe_done(request, contact_uuid):
    """display a thank-you message after emailing subscription"""
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    subscription_type_names = [
        subscription.subscription_type.name for subscription in contact.subscription_set.all()
    ]
    my_company = ', '.join(subscription_type_names)
    if not my_company:
        my_company = getattr(settings, 'BALAFON_MY_COMPANY', '')

    return render(
        request,
        'Emailing/public/subscribe_done.html',
        {
            'contact': contact,
            'my_company': my_company,
        }
    )


def subscribe_error(request, contact_uuid):
    """display an error message if emailing subscription fails"""
    contact = get_object_or_404(Contact, uuid=contact_uuid)
    subscription_type_names = [
        subscription.subscription_type.name for subscription in contact.subscription_set.all()
    ]
    my_company = ', '.join(subscription_type_names)
    if not my_company:
        my_company = getattr(settings, 'BALAFON_MY_COMPANY', '')

    return render(
        request,
        'Emailing/public/subscribe_error.html',
        {
            'contact': contact,
            'my_company': my_company,
        }
    )


def email_verification(request, contact_uuid):
    """handle click on verification link in email verification email"""
    try:
        contact = Contact.all_objects.get(uuid=contact_uuid)
    except (Contact.DoesNotExist, Contact.MultipleObjectsReturned):
        raise Http404
    subscription_type_names = [
        subscription.subscription_type.name for subscription in contact.subscription_set.all()
    ]
    redirect_to = request.GET.get('redirect_to', None)

    my_company = ', '.join(subscription_type_names)
    if not my_company:
        my_company = getattr(settings, 'BALAFON_MY_COMPANY', '')

    entity = contact.entity
    entity.confirmed = True
    entity.save()
    contact.confirmed = True
    contact.email_verified = True
    contact.save()

    if notify_subscription_on_confirmation():
        # send an email
        send_notification_email(request, contact, [], '')

    if redirect_to:
        return HttpResponseRedirect(redirect_to)
    else:
        return render(
            request,
            'Emailing/public/verification_done.html',
            {
                'contact': contact,
                'my_company': my_company,
            }
        )


def email_tracking(request, emailing_id, contact_uuid):
    """handle download of email opening tracking image"""
    emailing = get_object_or_404(models.Emailing, id=emailing_id)
    contact = get_object_or_404(Contact, uuid=contact_uuid)

    emailing.opened_emails.add(contact)
    emailing.save()

    dir_name = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(dir_name, "email-tracking.png")
    response = HttpResponse(FileWrapper(open(file_name, 'rb')), content_type='image/png')
    response['Content-Length'] = os.path.getsize(file_name)
    return response


class SubscribeView(View):
    """Subscribe to emailing"""
    template_name = 'Emailing/public/subscribe.html'

    def get_form_class(self):
        """get form: can be customized"""
        return get_subscription_form() or forms.SubscribeForm

    def get_template(self):
        """get template"""
        return self.template_name

    def is_enabled(self):
        return is_subscribe_enabled()

    @staticmethod
    def require_confirmation():
        return False

    def dispatch(self, request, *args, **kwargs):
        """make possible to disable this view from settings"""
        if not self.is_enabled():
            raise Http404
        return super(SubscribeView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self, contact):
        """where to redirect when form is valid"""
        return reverse('emailing_subscribe_done', args=[contact.uuid])

    def get_error_url(self, contact):
        """where to redirect on error"""
        return reverse('emailing_subscribe_error', args=[contact.uuid])

    def get_context_data(self, **kwargs):
        return {}

    def _display_form(self, form):
        """display form"""
        context_data = {
            'form': form,
        }
        context_data.update(self.get_context_data())
        return render(
            self.request,
            self.get_template(),
            context_data
        )

    def get(self, request, *args, **kwargs):
        """HTTP GET: display form"""
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        return self._display_form(form)

    def get_form_kwargs(self):
        """get this kwargs for form constructor"""
        return {}

    def post(self, request, *args, **kwargs):
        """HTTP POST: handle form"""

        form_class = self.get_form_class()

        form = form_class(request.POST, request.FILES, **self.get_form_kwargs())
        if form.is_valid():
            contact = form.save(request)
            if self.require_confirmation():
                contact.confirmed = False
                contact.save()
                entity = contact.entity
                entity.confirmed = False
                entity.save()
            try:
                subscription_queryset = contact.subscription_set.filter(accept_subscription=True)

                subscription_types = []
                for subscription in subscription_queryset:
                    new_subscription.send(sender=Subscription, instance=subscription, contact=contact)
                    subscription_types.append(subscription.subscription_type)

                send_verification_email(contact, subscription_types)
                return HttpResponseRedirect(self.get_success_url(contact))
            except EmailSendError:
                except_text = 'send_verification_email'
                logger.exception(except_text)

                # create action
                detail = _("An error occurred while verifying the email address of this contact.")
                fix_action = ActionType.objects.get_or_create(name=_('Balafon'))[0]
                action = Action.objects.create(
                    subject=_("Need to verify the email address"), planned_date=now_rounded(),
                    type=fix_action, detail=detail, display_on_board=True,
                )
                action.contacts.add(contact)
                action.save()

                return HttpResponseRedirect(self.get_error_url(contact))
        else:
            except_text = 'contact form : {0}'.format(form.errors)
            logger.warning(except_text)
        return self._display_form(form)


class EmailSubscribeView(SubscribeView):
    """Just a email field for newsletter subscription"""
    template_name = 'Emailing/public/subscribe_email.html'

    def is_enabled(self):
        return is_email_subscribe_enabled()

    @staticmethod
    def require_confirmation():
        return True

    def get_success_url(self, contact):
        """where to redirect when form is valid"""
        return reverse('emailing_subscribe_email_done')

    def get_error_url(self, contact):
        """where to redirect on error"""
        return reverse('emailing_subscribe_email_error')

    def get_form_kwargs(self, *args, **kwargs):
        """get this kwargs for form constructor"""
        form_kwargs = super(EmailSubscribeView, self).get_form_kwargs(*args, **kwargs)
        form_kwargs['subscription_type'] = self.kwargs.get('subscription_type', None)
        return form_kwargs

    def get_context_data(self, **kwargs):
        subscription_type_id = self.kwargs.get('subscription_type', None)
        if subscription_type_id:
            return {'action_url': reverse('emailing_email_subscribe_subscription', args=[subscription_type_id])}
        else:
            return {'action_url': reverse('emailing_email_subscribe_newsletter')}

    def get_form_class(self):
        """form class"""
        return forms.EmailSubscribeForm


class EmailSubscribeDoneView(TemplateView):
    """display subscription message"""
    template_name = 'Emailing/public/subscribe_email_done.html'


class EmailSubscribeErrorView(TemplateView):
    """display subscription error message"""
    template_name = 'Emailing/public/subscribe_email_error.html'


class EmailingUpdateView(UpdateView):
    """update an emailing settings"""
    template_name = 'Emailing/update_emailing.html'
    form_class = forms.UpdateEmailingForm
    model = models.Emailing

    def get_success_url(self):
        """redirect to this on success"""
        return reverse('emailing_view', args=[self.kwargs['pk']])

    @method_decorator(user_passes_test(can_access))
    @method_decorator(popup_redirect)
    def dispatch(self, *args, **kwargs):
        """subclass dispatch for decorators"""
        return super(EmailingUpdateView, self).dispatch(*args, **kwargs)
