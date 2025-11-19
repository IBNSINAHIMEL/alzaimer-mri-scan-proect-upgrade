// Page transitions
function fadePageOut(destination) {
    document.body.style.opacity = '0';
    setTimeout(() => {
        window.location.href = destination;
    }, 500);
}

// Parallax effects
function initParallax() {
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.parallax-bg');
        if (parallax) {
            parallax.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });
}

// Interactive charts
function initCharts() {
    // Use Chart.js for patient analytics
    const ctx = document.getElementById('patientChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Cognitive Score',
                data: [85, 82, 78, 75, 80],
                borderColor: '#4f46e5',
                tension: 0.3
            }]
        }
    });
}