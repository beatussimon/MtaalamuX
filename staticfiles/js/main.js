$(document).ready(function() {
    // Smooth scroll
    $('a.nav-link').on('click', function(event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800);
        }
    });

    // Auto-scroll chat box
    const chatBox = document.getElementById('chat-box');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});