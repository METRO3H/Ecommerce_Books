<?php

if (! defined('WP_DEBUG')) {
	die( 'Direct access forbidden.' );
}

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style( 'parent-style', get_template_directory_uri() . '/style.css' );
});

add_action('wp_enqueue_scripts', function(){
	wp_enqueue_style('child-style', get_stylesheet_uri());
});

function enqueue_custom_styles() {
    // Encolar el archivo CSS de Swiper
    wp_enqueue_style(
        'swiper-css', // Handle único para el archivo CSS
        'https://cdn.jsdelivr.net/npm/swiper@8/swiper-bundle.min.css', // URL del archivo CSS
        array(), // Dependencias (si hay alguna)
        null, // Versión (puedes usar null para que no se cachee)
        'all' // Medios (todos los medios en este caso)
    );
}
add_action('wp_enqueue_scripts', 'enqueue_custom_styles');


	function hello_world_shortcode() {
		return '<div id="carousel-container">
    <div>
      <span>discover</span>
      <h1>aquatic animals</h1>
      <hr />
      <p>
        Beauty and mystery are hidden under the sea. Explore with our application to know about
        Aquatic Animals.
      </p>
      <a href="#">download app</a>
    </div>
    <div class="swiper">
      <div class="swiper-wrapper">
        <div class="swiper-slide swiper-slide--one">
          <div>
            <h2>Jellyfish</h2>
            <p>
              Jellyfish and sea jellies are the informal common names given to the medusa-phase of
              certain gelatinous members of the subphylum Medusozoa, a major part of the phylum
              Cnidaria.
            </p>
            <a href="https://en.wikipedia.org/wiki/Jellyfish" target="_blank">explore</a>
          </div>
        </div>
        <div class="swiper-slide swiper-slide--two">
          <div>
            <h2>Seahorse</h2>
            <p>
              Seahorses are mainly found in shallow tropical and temperate salt water throughout
              the world. They live in sheltered areas such as seagrass beds, estuaries, coral
              reefs, and mangroves. Four species are found in Pacific waters from North America to
              South America.
            </p>
            <a href="https://en.wikipedia.org/wiki/Seahorse" target="_blank">explore</a>
          </div>
        </div>

        <div class="swiper-slide swiper-slide--three">
          <div>
            <h2>octopus</h2>
            <p>
              Octopuses inhabit various regions of the ocean, including coral reefs, pelagic
              waters, and the seabed; some live in the intertidal zone and others at abyssal
              depths. Most species grow quickly, mature early, and are short-lived.
            </p>
            <a href="https://en.wikipedia.org/wiki/Octopus" target="_blank">explore</a>
          </div>
        </div>

        <div class="swiper-slide swiper-slide--four">
          <div>
            <h2>Shark</h2>
            <p>
              Sharks are a group of elasmobranch fish characterized by a cartilaginous skeleton,
              five to seven gill slits on the sides of the head, and pectoral fins that are not
              fused to the head.
            </p>
            <a href="https://en.wikipedia.org/wiki/Shark" target="_blank">explore</a>
          </div>
        </div>

        <div class="swiper-slide swiper-slide--five">
          <div>
            <h2>Dolphin</h2>
            <p>
              Dolphins are widespread. Most species prefer the warm waters of the tropic zones,
              but some, such as the right whale dolphin, prefer colder climates. Dolphins feed
              largely on fish and squid, but a few, such as the orca, feed on large mammals such
              as seals.
            </p>
            <a href="https://en.wikipedia.org/wiki/Dolphin" target="_blank">explore</a>
          </div>
        </div>
      </div>
      <!-- Add Pagination -->
      <div class="swiper-pagination"></div>
    </div>
    <img
      src="https://cdn.pixabay.com/photo/2021/11/04/19/39/jellyfish-6769173_960_720.png"
      alt=""
      class="bg"
    />
    <img
      src="https://cdn.pixabay.com/photo/2012/04/13/13/57/scallop-32506_960_720.png"
      alt=""
      class="bg2"
    />
  </div>
  <!-- partial -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Swiper/8.4.5/swiper-bundle.min.js"></script>
  <script>
    /*
inspiration
https://dribbble.com/shots/4684682-Aquatic-Animals
*/

var swiper = new Swiper(".swiper", {
effect: "coverflow",
grabCursor: true,
centeredSlides: true,
coverflowEffect: {
  rotate: 0,
  stretch: 0,
  depth: 100,
  modifier: 3,
  slideShadows: true
},
keyboard: {
  enabled: true
},
mousewheel: {
  thresholdDelta: 70
},
loop: true,
pagination: {
  el: ".swiper-pagination",
  clickable: true
},
breakpoints: {
  640: {
    slidesPerView: 2
  },
  768: {
    slidesPerView: 1
  },
  1024: {
    slidesPerView: 2
  },
  1560: {
    slidesPerView: 3
  }
}
});
  </script>';
	}

	add_shortcode('hello_world', 'hello_world_shortcode');

function custom_search_input() {
	
    if (is_shop()) {
        ?>
        <script type="text/javascript">
        function do_the_thing(searchInput) {
            const searchInputDiv = searchInput.parentElement;
			console.log("BOB")
            // Verificar si ya existe el SVG
            if (!searchInputDiv.querySelector('svg.icon')) {
                searchInputDiv.classList.add("group");

                // Crear el nuevo SVG y el input
                const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svgIcon.classList.add("search-icon");
                svgIcon.setAttribute('aria-hidden', 'true');
                svgIcon.setAttribute('viewBox', '0 0 24 24');
                svgIcon.innerHTML = '<g><path d="M21.53 20.47l-3.66-3.66C19.195 15.24 20 13.214 20 11c0-4.97-4.03-9-9-9s-9 4.03-9 9 4.03 9 9 9c2.215 0 4.24-.804 5.808-2.13l3.66 3.66c.147.146.34.22.53.22s.385-.073.53-.22c.295-.293.295-.767.002-1.06zM3.5 11c0-4.135 3.365-7.5 7.5-7.5s7.5 3.365 7.5 7.5-3.365 7.5-7.5 7.5-7.5-3.365-7.5-7.5z"></path></g>';

                searchInputDiv.prepend(svgIcon);

                searchInput.classList.add("search-input");
                searchInput.setAttribute('placeholder', 'Buscar...');
            }
        }

        document.addEventListener("DOMContentLoaded", function() {
            let executed = false; // Variable para controlar la ejecución

            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (!executed && mutation.addedNodes.length) {
                        const searchInput = document.querySelector('.ui-autocomplete-input');
                        if (searchInput) {
                            do_the_thing(searchInput);
                            executed = true; // Marcar como ejecutado
                            observer.disconnect(); // Detenemos el observador una vez encontrado el elemento
                        }
                    }
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });
        });
        </script>
        <?php
    }
}

add_action('wp_footer', 'custom_search_input');



