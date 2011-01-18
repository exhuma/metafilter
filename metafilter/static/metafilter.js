$(document).ready(function() {
     $('.query-edit').editable('/save_query', {
         cssclass: 'query-edit-box'
        });
});

function set_rating(element, path, value){
   $.ajax({
      url: "/set_rating",
      type: "POST",
      data: {path: path, value: value},
      success: function(){element.addClass("active_rating");}
         })
}
