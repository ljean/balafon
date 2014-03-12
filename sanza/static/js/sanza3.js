$(function() {
    $(".dropdown-menu > li > a.disabled").click(function() {
        return false;
    });
    
    try {
        $(".chosen-select").chosen({disable_search: false, width: "50%"});
    } catch(e) {

    }
    
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
    
    $(".favorite-icon").live('click', function() {
        var form = $(this).find('form');
        var elt = $(this);
        $.ajax({
            type: "POST",
            url: form.attr('action'),
            dataType: 'json',
            data: form.serialize(),
            success: function(data) {
                if (data.success) {
                    var glyphicon = elt.find(".glyphicon");
                    glyphicon.removeClass('glyphicon-star').removeClass('glyphicon-star-empty');
                    glyphicon.addClass(data.status?'glyphicon-star':'glyphicon-star-empty');
                } else {
                    alert(data.message);
                }
            }
        });
        return false;
    })
})