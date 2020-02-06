$(function() {

    // multilines for navbar
    setTimeout(function () {
        var height = $("body > .navbar .navbar-collapse").height();
        $("#document").css('margin-top', height - 60);
    }, 100);


    $.fn.serializeForm = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return JSON.stringify(o);
        //return o;
    };
    
    $(".dropdown-menu > li > a.disabled").click(function() {
        return false;
    });
    
    $(".chosen-select").each(function (idx, elt) {
        var attrs = {
            disable_search: false,
        };
        var width = $(elt).attr('width');
        console.log('> width', width);
        if (width) {
            attrs.width = width;
        }
        try {
            $(elt).chosen(attrs);
        } catch(e) {
            console.error(e);
        }
    });

    
    $(".contenteditable").blur(function() {
        var t = (new Date()).getTime();
        var _that = $(this);
        $.ajax({
            type: "POST",
            url: $(this).attr('rel')+"?t="+t,
            data: {value: $(this).html()},
            success: function(data) {
                if (data.ok) {
                    //var elt = _that.after('<span class="success glyphicon glyphicon-saved"></span>');
                    var elt = $('<span class="label label-sm label-success"><span class="glyphicon glyphicon-saved"></span></span>').insertAfter(_that);
                    setTimeout(function() {elt.remove();}, 1000);
                } else {
                    var elt = $('<span class="label label-sm label-danger"></span>').insertAfter(_that);
                    //elt.attr("title", data.error);
                    elt.html('<span class="glyphicon glyphicon-warning-sign"> '+data.error+'</span>');
                }
            },
            dataType: 'json'
        });
    });
    
    $(".show-note").click(function() {
        $(this).closest(".action").find(".action-note").toggle();
        return false;  
    });
    
    $(".section-buttons ul.dropdown-menu").each(function(idx, elt) {
        if ($(this).find("li").length==0) {
            $(this).closest(".section-buttons").hide();
        }
    });
    
    $(document).on('click', ".favorite-icon", function() {
        var form = $(this).find('form');
        var elt = $(this);
        $.ajax({
            type: "POST",
            url: form.attr('action'),
            dataType: 'json',
            data: form.serialize(),
            success: function(data) {
                if (data.success) {
                    var icon = elt.find(".fa-star");
                    icon.removeClass('fas').removeClass('far');
                    icon.addClass(data.status?'fas':'far');
                } else {
                    alert(data.message);
                }
            }
        });
        return false;
    })
    
    $(".letter-filter").click(function() {
      var loc = window.location;
      var entitiesListUrl = $(this).closest('.letter-bar').attr('rel');
      var url = loc.protocol + '//' + loc.host + entitiesListUrl; // loc.pathname;
      window.location = url+"?filter="+$(this).attr('rel');
      return false;
    });
    
    $(".make-homepage").click(function() {
        var elt = $(this);
        var loc = window.location;
        var url = loc.protocol + '//' + loc.host + loc.pathname;
        if ($(this).attr('rel')) {
          $.ajax({
              type: "POST",
              url: $(this).attr('rel'),
              dataType: 'json',
              data: {'url': url},
              success: function(data) {
                  if (data.ok) {
                      elt.addClass("success");
                  } else {
                      elt.addClass("error");
                      alert(data.message);
                  }
              }
          });
        }
        return false;
    })
})