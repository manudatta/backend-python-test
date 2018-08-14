// Example starter JavaScript for disabling form submissions if there are invalid fields
(function() {
  'use strict';
  window.addEventListener('load', function() {
    $("input[type='checkbox']").change(function(e) {
      var todo_id = this.value;
      var is_checked = this.checked;
      var data = { 'done' : is_checked };
      $.ajax({
        url : todo_id,
        data : data,
        type : 'PATCH'
      });
    });
  }, false);
})();
