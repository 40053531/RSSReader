$.get('http://stackoverflow.com/feeds/question/10943544', function (data){
  $(data).find("entry).each(function(){
    var el = $(this);
   
    $('.RSSTitle').html("Title    :"+el.find("title").text());
    $('.RSSAuthor').html("Author  :"+el.find("author").text());
    $('.RSSDescription').html("Desc:    "+el.find("description").text());
  });
});
