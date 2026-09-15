$(document).ready(function() {
  var li = $('<li><a href="#" id="contact-nav-link" class="nav-link">Contact</a></li>');
  $('.navbar-nav').append(li);
  $('#contact-nav-link').on('click', function(e) {
    e.preventDefault();
    Shiny.setInputValue('open_contact', Math.random(), {priority: 'event'});
  });
});
