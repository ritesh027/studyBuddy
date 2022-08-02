console.log("hello");
const dropdownMenu = document.querySelector('.dropdown-menu');
const dropdownButton = document.querySelector('.dropdown-button');

if (dropdownButton) {
  dropdownButton.addEventListener('click', (e) => {
    console.log('clicked');
    dropdownMenu.classList.toggle('show');
  });
}
