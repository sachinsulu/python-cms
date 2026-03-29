/* ===========================================

01. ScrollIt
02. Preloader
03. Navbar scrolling background
04. Close navbar-collapse when a clicked
05. Custom owl-nav
06. Sections data-background image
07. Slider & Slider-Fade owlCarousel
08. Image Gallery Scroll owlCarousel
09. Clients owlCarousel
10. Testimonials owlCarousel
11. Rooms 1 owlCarousel
12. Rooms 2 owlCarousel
13. Rooms 3 owlCarousel
14. Blog 1 owlCarousel
15. Restaurant Menu owlCarousel
16. Restaurant Menu Tabs
17. Magnific Popup
18. Accordion (F.A.Qs)
19. Animations
20. Video Text
21. Pricing
22. Offers 2
23. Services Accordion
24. YouTubePopUp
25. Scroll back to top
26. Button

=========================================== */

$(function () {
    "use strict";
    var wind = $(window);
    
    // ScrollIt
    $.scrollIt({
        upKey: 38, // key code to navigate to the next section
        downKey: 40, // key code to navigate to the previous section
        easing: 'swing', // the easing function for animation
        scrollTime: 600, // how long (in ms) the animation takes
        activeClass: 'active', // class given to the active nav element
        onPageChange: null, // function(pageIndex) that is called when page is changed
        topOffset: -70 // offste (in px) for fixed top navigation
    });
    
    // Preloader
    $(window).load(function() {
        $('.preloader').delay(100).fadeOut("slow");
    });

    // Navbar scrolling background
    wind.on("scroll", function () {
        var bodyScroll = wind.scrollTop()
            , navbar = $(".navbar")
            , logo = $(".navbar .logo> img");
        if (bodyScroll > 100) {
            navbar.addClass("nav-scroll");
            logo.attr('src', '/static/img/logo.png');
        }
        else {
            navbar.removeClass("nav-scroll");
            logo.attr('src', '/static/img/logo.png');
        }
    });
    
    // Close navbar-collapse when a clicked
    $(".navbar-nav .dropdown-item a").on('click', function () {
        $(".navbar-collapse").removeClass("show");
    });
    
    /* Custom owl-nav */
    var selector = $('.rooms1 .owl-carousel');
    $('.my-next-button').click(function() {
      selector.trigger('next.owl.carousel');
    });
    $('.my-prev-button').click(function() {
      selector.trigger('prev.owl.carousel');
    });
    
    // Sections data-background image
    var pageSection = $(".bg-img, section");
    pageSection.each(function (indx) {
        if ($(this).attr("data-background")) {
            $(this).css("background-image", "url(" + $(this).data("background") + ")");
        }
    });
    
    // Slider & Slider-Fade owlCarousel
    $(document).ready(function () {
        var owl = $('.header .owl-carousel');
        // Slider owlCarousel - (Inner Page Slider)
        $('.slider .owl-carousel').owlCarousel({
            items: 1
            , loop: true
            , dots: true
            , margin: 0
            , autoplay: false
            , autoplayTimeout: 5000
            , nav: true
            , navText: ['<i class="fa-light fa-angle-left" aria-hidden="true"></i>', '<i class="fa-light fa-angle-right" aria-hidden="true"></i>']
            , responsiveClass: true
            , responsive: {
                0: {
                    dots: false
                , }
                , 600: {
                    dots: false
                , }
                , 1000: {
                    dots: false
                , }
            }
        });
        $('.slider-fade .owl-carousel').owlCarousel({
            items: 1
            , loop: true
            , dots: true
            , margin: 0
            , autoplay: false
            , autoplayTimeout: 5000
            , animateOut: 'fadeOut'
            , nav: true
            , navText: ['<i class="fa-light fa-angle-left" aria-hidden="true"></i>', '<i class="fa-light fa-angle-right" aria-hidden="true"></i>']
        });
        owl.on('changed.owl.carousel', function (event) {
            var item = event.item.index - 2; // Position of the current item
            $('h5').removeClass('animated fadeInUp');
            $('h1').removeClass('animated fadeInUp');
            $('p').removeClass('animated fadeInUp');
            $('.date').removeClass('animated fadeInUp');
            $('.button-1').removeClass('animated fadeInUp');
            $('.button-2').removeClass('animated fadeInUp');
            $('.owl-item').not('.cloned').eq(item).find('h5').addClass('animated fadeInUp');
            $('.owl-item').not('.cloned').eq(item).find('h1').addClass('animated fadeInUp');
            $('.owl-item').not('.cloned').eq(item).find('p').addClass('animated fadeInUp');
            $('.owl-item').not('.cloned').eq(item).find('.date').addClass('animated fadeInUp');
            $('.owl-item').not('.cloned').eq(item).find('.button-1').addClass('animated fadeInUp');
            $('.owl-item').not('.cloned').eq(item).find('.button-2').addClass('animated fadeInUp');
        });
    });
    
    // Image Gallery Scroll owlCarousel
    $('.galleryscroll .owl-carousel').owlCarousel({
        loop: true
         , margin: 20
        , mouseDrag: true
        , autoplay: true
        , autoplayTimeout: 4000
        , smartSpeed: 1000
        , dots: false
        , nav: false
        , navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"]
        , autoplayHoverPause: true
        , responsiveClass: true
        , responsive: {
            0: {
                items: 1
            , }
            , 600: {
                items: 1
            , }
            , 1000: {
                items: 3
            , }
        }
    });
    
    // Clients owlCarousel
    $('.clients .owl-carousel').owlCarousel({
        loop: true
        , margin: 20
        , mouseDrag: true
        , autoplay: true
        , autoplayTimeout: 5000
        , dots: false
        , autoplayHoverPause: true
        , nav: false
        , navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"]
        , responsiveClass: true
        , responsive: {
            0: {
                items: 1
            , }
            , 600: {
                items: 1
            , }
            , 1000: {
                items: 5
            , }
        }
    });
    
    // Testimonials owlCarousel
    $('.testimonials .owl-carousel').owlCarousel({
        loop: true
        , margin: 20
        , mouseDrag: true
        , autoplay: false
        , autoplayTimeout: 5000
        , dots: true
        , autoplayHoverPause: true
        , nav: false
        , navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"]
        , responsiveClass: true
        , responsive: {
            0: {
                items: 1
            , }
            , 600: {
                items: 1
            , }
            , 1000: {
                items: 2
            , }
        }
    });
    
    // Rooms 1 owlCarousel
    $('.rooms1 .owl-carousel').owlCarousel({
        loop: true
        , items: 2 
        , margin: 20
        , mouseDrag: true
        , autoplay: false
        , autoplayTimeout: 5000
        , dots: false
        , autoplayHoverPause: true
        , nav: false
        , navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"]
        , responsiveClass: true
        , responsive: {
            0: {
                items: 1
            , }
            , 600: {
                items: 1
            , }
            , 1000: {
                items: 2
            , }
        }
    });
    
    // Rooms 2 owlCarousel
    $('.rooms2 .owl-carousel').owlCarousel({
        loop: true,
        margin: 30,
        mouseDrag: true,
        autoplay: false,
        autoplayTimeout: 5000,
        dots: true,
        nav: true,
        navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"],
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
                nav: false,
            },
            600: {
                items: 1,
                nav: false,
            },
            1000: {
                items: 1
            }
        }
    });
    
    // Rooms 3
    $('.rooms3 .owl-carousel').owlCarousel({
        stagePadding: 30
        , loop: true
        , margin: 30
        , mouseDrag: true
        , autoplay: false
        , autoplayTimeout: 5000
        , dots: false
        , nav: true
        , navText: ['<i class="fa-light fa-angle-left"></i>', '<i class="fa-light fa-angle-right"></i>']
        , autoplayHoverPause:true
        , responsiveClass: true
        , responsive:{
            0:{
                items: 1,
                stagePadding: 0,
                nav: false,
            },
            600:{
                items: 1,
                stagePadding: 0,
                nav: false,
            },
            1000:{
                items: 1,
                stagePadding: 300
            }
        }
})
    
    
    // Restaurant Menu owlCarousel 
    $('.restaurant-menu .owl-carousel').owlCarousel({
        loop: true,
        margin: 0,
        autoplay: false,
        autoplayTimeout: 5000,
        dots: false,
        nav: true,
        navText: ["<span class='lnr ti-angle-left'></span>","<span class='lnr ti-angle-right'></span>"],
        responsiveClass: true,
        responsive: {
            0: {
                items: 2,
                nav: false
            },
            600: {
                items: 3,
                nav: false
            },
            1000: {
                items: 4
            }
        }
    });
    
    // Restaurant Menu Tabs
    $(".restaurant-menu .tabs-icon").on("click", ".item", function () {
        $(".item").removeClass("active");
        var myID = $(this).attr("id");
        $(".restaurant-menu .cont").hide();
        $("#" + myID + "-content").fadeIn();
    });
    $(".restaurant-menu .tabs-icon").on("click", ".owl-item", function () {
        $(this).addClass("actived").siblings().removeClass("actived");
    });
    
    
    // Team owlCarousel
    $('.team .owl-carousel').owlCarousel({
        loop: true
        , margin: 20
        , mouseDrag: true
        , autoplay: false
        , autoplayTimeout: 5000
        , dots: true
        , autoplayHoverPause: true
        , nav: false
        , navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"]
        , responsiveClass: true
        , responsive: {
            0: {
                items: 1,
                nav: false,
                dots: true
            , }
            , 600: {
                items: 2,
                nav: false,
                dots: true
            , }
            , 1000: {
                items: 4
            , }
        }
    });
    
    // Blog 1 owlCarousel
    $('.blog1 .owl-carousel').owlCarousel({
        loop: true
        , margin: 20
        , mouseDrag: true
        , autoplay: false
        , autoplayTimeout: 5000
        , dots: false
        , autoplayHoverPause: true
        , nav: true
        , navText: ["<span class='fa-light fa-angle-left'></span>", "<span class='fa-light fa-angle-right'></span>"]
        , responsiveClass: true
        , responsive: {
            0: {
                items: 1,
                nav: false,
                dots: true
            , }
            , 600: {
                items: 2,
                nav: false,
                dots: true
            , }
            , 1000: {
                items: 3
            , }
        }
    });
    
    // Magnific Popup
    $(".img-zoom").magnificPopup({
        type: "image"
        , closeOnContentClick: !0
        , mainClass: "mfp-fade"
        , gallery: {
            enabled: !0
            , navigateByImgClick: !0
            , preload: [0, 1]
        }
    })
    $('.magnific-youtube, .magnific-vimeo, .magnific-custom').magnificPopup({
        disableOn: 700
        , type: 'iframe'
        , mainClass: 'mfp-fade'
        , removalDelay: 300
        , preloader: false
        , fixedContentPos: false
    });
    
    // Accordion (F.A.Qs)
    if ($(".accordion-box").length) {
        $(".accordion-box").on("click", ".acc-btn", function () {
            var outerBox = $(this).parents(".accordion-box");
            var target = $(this).parents(".accordion");
            if ($(this).next(".acc-content").is(":visible")) {
                //return false;
                $(this).removeClass("active");
                $(this).next(".acc-content").slideUp(200);
                $(outerBox).children(".accordion").removeClass("active-block");
            }
            else {
                $(outerBox).find(".accordion .acc-btn").removeClass("active");
                $(this).addClass("active");
                $(outerBox).children(".accordion").removeClass("active-block");
                $(outerBox).find(".accordion").children(".acc-content").slideUp(200);
                target.addClass("active-block");
                $(this).next(".acc-content").slideDown(200);
            }
        });
    }
    
    // Animations
    var contentWayPoint = function () {
        var i = 0;
        $('.animate-box').waypoint(function (direction) {
            if (direction === 'down' && !$(this.element).hasClass('animated')) {
                i++;
                $(this.element).addClass('item-animate');
                setTimeout(function () {
                    $('body .animate-box.item-animate').each(function (k) {
                        var el = $(this);
                        setTimeout(function () {
                            var effect = el.data('animate-effect');
                            if (effect === 'fadeIn') {
                                el.addClass('fadeIn animated');
                            }
                            else if (effect === 'fadeInLeft') {
                                el.addClass('fadeInLeft animated');
                            }
                            else if (effect === 'fadeInRight') {
                                el.addClass('fadeInRight animated');
                            }
                            else {
                                el.addClass('fadeInUp animated');
                            }
                            el.removeClass('item-animate');
                        }, k * 200, 'easeInOutExpo');
                    });
                }, 100);
            }
        }, {
            offset: '85%'
        });
    };
    $(function () {
        contentWayPoint();
    });

    // Video Text
    letterCarousel('.video-wrapper', '.video-text');
    function letterCarousel(parent_cls, child_cls) {
        var e = jQuery(parent_cls + ' ' + child_cls)
            , t = jQuery(window).height();
        jQuery(window).on("scroll", function () {
            if (jQuery(parent_cls).length) {
                var t = jQuery(document).scrollTop() + jQuery(window).height()
                    , n = jQuery(parent_cls).offset().top;
                if (n <= t) {
                    var i = jQuery(document).scrollTop() - n + jQuery(window).height();
                    var scroll = i - 150;
                    var scroll_slow = scroll + ((scroll / 70) / 100);
                    var img_scroll = scroll_slow * 30 / 100;
                    e.css({
                        transform: "translateX(" + img_scroll + "px)"
                    })
                }
            }
        });
    }
    

    // Pricing
    $('.pricing').each(function(index, value) {
            var radix = $(value),
                totalWidth = radix.outerWidth(),
                slidingLength = radix.find('.item').length,
                devideRightPadding = parseInt(radix.css('padding-right')) / slidingLength,
                devideLeftPadding = parseInt(radix.css('padding-left')) / slidingLength,
                usageWidth = (slidingLength * 30) + 30 + devideRightPadding + devideLeftPadding,
                useWidth = totalWidth - usageWidth,
                devideLength = slidingLength + 1,
                devideWidth = (useWidth / devideLength),
                activeWidth = devideWidth * 2;
            radix.find('.item, .img, .item .cont').css('width', devideWidth);
            radix.find('.item .cont').css('left', devideWidth);
            radix.find('.item.active').css('width', activeWidth);
            $(document).on('mouseenter', '.pricing .item', function() {
                $(this).siblings().removeClass('active');
                $(this).addClass('active');
                radix.find('.item, .img, .item .cont').css('width', devideWidth);
                radix.find('.item .cont').css('left', devideWidth);
                radix.find('.item.active').css('width', activeWidth);
            });
        });
    
    // Offers 2 
    $('.offers2 .item').on('mouseenter click', function () {
        var tab_id = $(this).attr('data-tab');
        $('.offers2 .item').removeClass('current');
        $(this).addClass('current');

        $('.glry-img .tab-img ').removeClass('current');
        $("#" + tab_id).addClass('current');

        if ($(this).hasClass('current')) {
            return false;
        }
    });
    
    // Facilities 2
    if ($(".facilities2").length) {
        $(".facilities2 .tab-buttons .tab-btn").on("click", function (e) {
          e.preventDefault();
          var target = $($(this).attr("data-tab"));
          if ($(target).is(":visible")) {
            return false;
          } else {
            target
              .parents(".facilities2")
              .find(".tab-buttons")
              .find(".tab-btn")
              .removeClass("active-btn");
            $(this).addClass("active-btn");
            target
              .parents(".facilities2")
              .find(".tabs-content")
              .find(".tab")
              .fadeOut(0);
            target
              .parents(".facilities2")
              .find(".tabs-content")
              .find(".tab")
              .removeClass("active-tab");
            $(target).fadeIn(300);
            $(target).addClass("active-tab");
          }
        });
      }
    
    // YouTubePopUp
    $("a.vid").YouTubePopUp();
    
    // Scroll back to top
    var progressPath = document.querySelector('.progress-wrap path');
    var pathLength = progressPath.getTotalLength();
    progressPath.style.transition = progressPath.style.WebkitTransition = 'none';
    progressPath.style.strokeDasharray = pathLength + ' ' + pathLength;
    progressPath.style.strokeDashoffset = pathLength;
    progressPath.getBoundingClientRect();
    progressPath.style.transition = progressPath.style.WebkitTransition = 'stroke-dashoffset 10ms linear';
    var updateProgress = function () {
        var scroll = $(window).scrollTop();
        var height = $(document).height() - $(window).height();
        var progress = pathLength - (scroll * pathLength / height);
        progressPath.style.strokeDashoffset = progress;
    }
    updateProgress();
    $(window).scroll(updateProgress);
    var offset = 150;
    var duration = 550;
    jQuery(window).on('scroll', function () {
        if (jQuery(this).scrollTop() > offset) {
            jQuery('.progress-wrap').addClass('active-progress');
        }
        else {
            jQuery('.progress-wrap').removeClass('active-progress');
        }
    });
    jQuery('.progress-wrap').on('click', function (event) {
            event.preventDefault();
            jQuery('html, body').animate({
                scrollTop: 0
            }, duration);
            return false;
        })
    
    // Select2
    $('.select2').select2({
        minimumResultsForSearch: Infinity,
    });
    
    // Datepicker
    $(".datepicker").datepicker({
        orientation: "top"
    });
    
    // Button
        var buttons = document.querySelectorAll(".button-1, .button-2, button-3, btn-form1-submit, tab-btn, .curv-butn");
        for(var i = 0; i < buttons.length; i++) {
          var button = buttons[i];
          button.addEventListener("click", function() {
            if(!button.classList.contains("active"))
              button.classList.add("active");
            else
              button.classList.remove("active");
          });
        }
    
}());


