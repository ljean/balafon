$(function() {
    $(".dropdown-menu > li > a.disabled").click(function() {
        return false;
    });
    
    $(".chosen-select").chosen();
})