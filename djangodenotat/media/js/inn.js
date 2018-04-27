(function( jQuery ) {
  jQuery.fn.hasAttr = function( name ) {
      for ( var i = 0, l = this.length; i < l; i++ ) {
          if ( !!( this.attr( name )) ) {
              return true;
          }
      }
      return false;
  };
})( jQuery );




$(document).ready(function() {
    $('#send').ajaxForm({
      dataType: 'json',
      success: function(data) {
        const trans = $('td#trans');
        trans.empty();
        trans.text(data.trans);
      }
    });

    function show(formData, jqForm, options) {
        $('td#progress').css("display","");
        return true;
    }

    function showbleu(formData, jqForm, options) {
        $('td#bleu-progress').css("display","");
        return true;
    }

    $('#load').ajaxForm({
      dataType: 'json',
      beforeSubmit: show,
      //error: alert("Прогнило что-то в датском королевстве..."),
      success: function(data) {
        $('td#progress').css("display","none");
        alert("Словарь успешно составлен!");
        location.reload();
      }
    });

    $('#bleu').ajaxForm({
      dataType: 'json',
      beforeSubmit: showbleu,
        //error: alert("Ошибка вычислений!"),
      success: function(data) {
        $('td#bleu-progress').css("display","none");
        alert("BLEU = "+data.bleu);
        location.reload();
      }
    });

});