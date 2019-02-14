$(function(){
  $("#search-input").keyup(function(){
    var searchInput = $(this).val();
    console.log($(this).val());
    $.ajax({
      url: "/search",
      data: {"name": searchInput},
      success: function(res){
        $("#search-results").html(res);
      }
    });
  })
});