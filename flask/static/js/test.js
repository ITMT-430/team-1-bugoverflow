jQuery(document).ready(function($){

$('#submit-comment').prop('disabled', true);

$('textarea').on('keyup',function() {
    var textarea_value = $("#comment").val();
    
    if(textarea_value != '') {
        $('#submit-comment').prop('disabled' , false);
    }else{
        $('#submit-comment').prop('disabled' , true);
    }
});

});