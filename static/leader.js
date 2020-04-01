var button1 = document.querySelector('#seepos')
button1.onclick = function(){
    document.getElementById('hidden').style.display = 'block';
    document.getElementById('hidden1').style.opacity = 1;
    this.style.display = 'none';
}
$(window).on("load resize ", function() {
    var scrollWidth = $('.tbl-content').width() - $('.tbl-content table').width();
    $('.tbl-header').css({'padding-right':scrollWidth});
  }).resize();
 
