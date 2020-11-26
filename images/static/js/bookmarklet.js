(function(){
  var jquery_version = '3.4.1';
  var site_url = 'https://127.0.0.1:8000/';
  var static_url = site_url + 'static/';
  var min_width = 100;
  var min_height = 100;

  function bookmarklet(msg) {
    // загрузить CSS
    var css = jQuery('<link>');
    css.attr({
      rel: 'stylesheet',
      type: 'text/css',
      href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random()*99999999999999999999)
    });
    jQuery('head').append(css);

    // загрузить HTML
    box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>Выберите изображение для закладки:</h1><div class="images"></div></div>';
    jQuery('body').append(box_html);

    // закрыть мероприятие
    jQuery('#bookmarklet #close').click(function(){
       jQuery('#bookmarklet').remove();
    });
    // найти изображения и отобразить их
    jQuery.each(jQuery('img[src$="jpg"]'), function(index, image) {
      if (jQuery(image).width() >= min_width && jQuery(image).height()
      >= min_height)
      {
        image_url = jQuery(image).attr('src');
        jQuery('#bookmarklet .images').append('<a href="#"><img src="'+
        image_url +'" /></a>');
      }
    });

    // когда изображение выбрано, откройте URL с ним
    jQuery('#bookmarklet .images a').click(function(e){
      selected_image = jQuery(this).children('img').attr('src');
      // скрыть букмарклет
      jQuery('#bookmarklet').hide();
      // открыть новое окно, чтобы отправить изображение
      window.open(site_url +'images/create/?url='
                  + encodeURIComponent(selected_image)
                  + '&title='
                  + encodeURIComponent(jQuery('title').text()),
                  '_blank');
    });

  };

  // Проверьте, загружен ли jQuery
  if(typeof window.jQuery != 'undefined') {
    bookmarklet();
  } else {
    // Проверить на конфликты
    var conflict = typeof window.$ != 'undefined';
    // Создайте скрипт и укажите на Google API
    var script = document.createElement('script');
    script.src = '//ajax.googleapis.com/ajax/libs/jquery/' +
      jquery_version + '/jquery.min.js';
    // Добавляем скрипт в 'head' для обработки
    document.head.appendChild(script);
    // Создайте способ дождаться загрузки скрипта
    var attempts = 15;
    (function(){
      // Проверьте еще раз, если jQuery не определен
      if(typeof window.jQuery == 'undefined') {
        if(--attempts > 0) {
          // Называет себя через несколько миллисекунд
          window.setTimeout(arguments.callee, 250)
        } else {
          // Слишком много попыток загрузки, ошибка отправки
          alert('Ошибка при загрузке jQuery')
        }
      } else {
          bookmarklet();
      }
    })();
  }
})()