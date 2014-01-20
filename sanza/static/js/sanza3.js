$(function() {
    $(".dropdown-menu > li > a.disabled").click(function() {
        return false;
    });
    
    try {
        $(".chosen-select").chosen({disable_search: false, width: "50%"});
    } catch(e) {
        //silence
    }
    
    $(".contenteditable").blur(function() {
        var _that = $(this);
        $.ajax({
            type: "POST",
            url: $(this).attr('rel'),
            data: {value: $(this).text()},
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
})