$(document).ready(function(){
  $("#search_btn").click(function(){
    var url = window.location.host + "/search/?q=" +term;
     window.location.assign(url);
     return true;
  
}}
