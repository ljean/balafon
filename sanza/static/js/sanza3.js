$(function() {
    $(".dropdown-menu > li > a.disabled").click(function() {
        return false;
    });
    
    try {
        $(".chosen-select").chosen({disable_search: false, width: "50%"});
    } catch(e) {
        //silence
    }
    
    
})