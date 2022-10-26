function goBack() {
    window.history.back();
}


var wHeight = $(window).innerHeight();

$(window).on('scroll', function () {
    var offset = $(this).scrollTop();

    if (offset > 10) {
        $('#navbar').addClass('fix');
        $('#navbar').removeClass('no_fix');
        $('#navbar1').addClass('fix_2');
        $('#navbar1').removeClass('no_fix_2');
    } else {
        $('#navbar').removeClass('fix');
        $('#navbar').addClass('no_fix');
        $('#navbar1').removeClass('fix_2');
        $('#navbar1').addClass('no_fix_2');
    }
});
