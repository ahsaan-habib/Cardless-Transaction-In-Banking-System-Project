document.addEventListener("DOMContentLoaded", () => {
  // window.addEventListener("scroll", () => {
  //   stickyNavbar();
  // });

  function stickyNavbar() {
    const topNavbar = document.querySelector("#top-navbar");
    const sticky = topNavbar.offsetTop;
    var body = document.body,
      html = document.documentElement;

    var height = Math.max(
      body.scrollHeight,
      body.offsetHeight,
      html.clientHeight,
      html.scrollHeight,
      html.offsetHeight
    );

    if (height > 1000 && window.pageYOffset >= sticky + 300) {
      topNavbar.classList.add("NavbarSticky");
    } else {
      topNavbar.classList.remove("NavbarSticky");
    }
  }

  /**
   * Testimonials slider
   */
  new Swiper(".testimonials-slider", {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    slidesPerView: "auto",
    pagination: {
      el: ".swiper-pagination",
      type: "bullets",
      clickable: true,
    },
    breakpoints: {
      320: {
        slidesPerView: 1,
        spaceBetween: 20,
      },

      1200: {
        slidesPerView: 3,
        spaceBetween: 20,
      },
    },
  });
});

/**
 * Animation on scroll
 */
window.addEventListener("load", () => {
  AOS.init({
    duration: 500,
    easing: "ease-in-out",
    once: true,
    mirror: false,
  });
});
