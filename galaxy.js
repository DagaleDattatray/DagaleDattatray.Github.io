const canvas = document.getElementById("galaxy-canvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let centerX = canvas.width / 2;
let centerY = canvas.height / 2;

window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  centerX = canvas.width / 2;
  centerY = canvas.height / 2;
});

const planets = [
  { name: "Mercury", radius: 3, distance: 40, speed: 0.04, color: "#b1b1b1" },
  { name: "Venus",   radius: 5, distance: 60, speed: 0.03, color: "#e0c97f" },
  { name: "Earth",   radius: 5.5, distance: 80, speed: 0.025, color: "#3e8ed0" },
  { name: "Mars",    radius: 4.5, distance: 100, speed: 0.02, color: "#c1440e" },
  { name: "Jupiter", radius: 10, distance: 130, speed: 0.015, color: "#d9a066" },
  { name: "Saturn",  radius: 9, distance: 160, speed: 0.012, color: "#e0c97f" },
  { name: "Uranus",  radius: 7, distance: 190, speed: 0.01, color: "#7dcfd8" },
  { name: "Neptune", radius: 7, distance: 220, speed: 0.008, color: "#4763c2" },
];

let angles = Array(planets.length).fill(0);

// Stars
const stars = Array.from({ length: 200 }, () => ({
  x: Math.random() * canvas.width,
  y: Math.random() * canvas.height,
  radius: Math.random() * 1.5,
  opacity: Math.random()
}));

// Comets
let comets = [];

function spawnComet() {
  if (Math.random() < 0.01) {
    comets.push({
      x: -50,
      y: Math.random() * canvas.height,
      vx: 4 + Math.random() * 2,
      vy: -1 + Math.random() * 2,
      radius: 2 + Math.random() * 2,
      opacity: 1
    });
  }
}

function drawStars() {
  stars.forEach(star => {
    ctx.beginPath();
    ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 255, 255, ${Math.sin(Date.now() / 500 + star.x) * 0.5 + 0.5})`;
    ctx.fill();
  });
}

function drawSun() {
  const gradient = ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, 60);
  gradient.addColorStop(0, "#fffacd");
  gradient.addColorStop(1, "#ffaa00");

  ctx.beginPath();
  ctx.fillStyle = gradient;
  ctx.shadowBlur = 50;
  ctx.shadowColor = "#ffaa00";
  ctx.arc(centerX, centerY, 30, 0, Math.PI * 2);
  ctx.fill();
}

function drawOrbits() {
  planets.forEach(planet => {
    ctx.beginPath();
    ctx.arc(centerX, centerY, planet.distance, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.lineWidth = 0.5;
    ctx.stroke();
  });
}

function drawPlanets() {
  planets.forEach((planet, i) => {
    angles[i] += planet.speed;
    const x = centerX + planet.distance * Math.cos(angles[i]);
    const y = centerY + planet.distance * Math.sin(angles[i]);

    ctx.beginPath();
    ctx.fillStyle = planet.color;
    ctx.shadowBlur = 10;
    ctx.shadowColor = planet.color;
    ctx.arc(x, y, planet.radius, 0, Math.PI * 2);
    ctx.fill();
  });
}

function drawComets() {
  comets.forEach((comet, i) => {
    ctx.beginPath();
    ctx.fillStyle = `rgba(255,255,255,${comet.opacity})`;
    ctx.shadowBlur = 20;
    ctx.shadowColor = "#ffffff";
    ctx.arc(comet.x, comet.y, comet.radius, 0, Math.PI * 2);
    ctx.fill();

    // Trail
    ctx.beginPath();
    const grad = ctx.createLinearGradient(comet.x, comet.y, comet.x - 30, comet.y - 5);
    grad.addColorStop(0, "rgba(255,255,255,0.4)");
    grad.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = grad;
    ctx.fillRect(comet.x - 30, comet.y - 2, 30, 4);

    comet.x += comet.vx;
    comet.y += comet.vy;
    comet.opacity -= 0.003;

    if (comet.opacity <= 0 || comet.x > canvas.width + 50) {
      comets.splice(i, 1);
    }
  });
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawStars();
  drawOrbits();
  drawSun();
  drawPlanets();
  drawComets();
  spawnComet();
  requestAnimationFrame(animate);
}

animate();
