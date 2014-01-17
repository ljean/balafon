$(function() {
    $(".dropdown-menu > li > a.disabled").click(function() {
        return false;
    });
    
    $(".chosen-select").chosen({disable_search: false, width: "50%"});
})