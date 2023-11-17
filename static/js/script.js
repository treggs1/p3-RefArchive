// Materialize Initialize
$(document).ready(function(){
    $('select').formSelect();
  });

// Nav JS this is a navbar I modified from another website I've been working on 
// originally modified from https://jit.codes/r/Ofcq7DgOjpxUzbny1NhVR
const burger = document.querySelector(".burger");
const nav = document.querySelector(".nav-links");
const navLinks = document.querySelectorAll(".nav-links a");

const navSlide = () => {
  burger.addEventListener("click", () => {
    nav.classList.toggle("nav-active");

    navLinks.forEach((link, index) => {
      if (link.style.animation) {
        link.style.animation = "";
      } else {
        link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.5}s`;
      }
    });

    burger.classList.toggle("toggle");
  });
};

navSlide();