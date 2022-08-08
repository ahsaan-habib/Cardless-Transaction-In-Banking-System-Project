document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector(".custom-file-input");
  const submitImageBtn = document.querySelector(".image-submit-btn");
  const errors = document.querySelector("#image-errors");

  input.addEventListener("change", function (e) {
    // var fileName = document.getElementById("inputImage").files[0].name;
    var nextSibling = e.target.nextElementSibling;
    nextSibling.style.display = "none";

    const file = document.querySelector("input[type=file]").files[0];
    readURL(file);
    submitImageBtn.style.display = "block";
    errors.style.display = "none";
  });

  document.getElementById("image-group").onclick = function (event) {
    document.getElementById("inputImage").click();
  };

  function readURL(input) {
    var reader = new FileReader();
    reader.onload = function (e) {
      $("#image_display").attr("src", e.target.result);
    };
    reader.readAsDataURL(input);
  }
});
