const profileToggle = document.getElementById('profileToggle');
const dropdownMenu = document.getElementById('dropdownMenu');

profileToggle.addEventListener('click', () => {
  dropdownMenu.style.display =
    dropdownMenu.style.display === 'flex' ? 'none' : 'flex';
  dropdownMenu.style.flexDirection = 'column';
});

window.addEventListener('click', (e) => {
  if (!profileToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
    dropdownMenu.style.display = 'none';
  }
});

const navLinks = document.querySelectorAll('#navLinks a');
navLinks.forEach(link => {
    link.addEventListener('click', function () {
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});