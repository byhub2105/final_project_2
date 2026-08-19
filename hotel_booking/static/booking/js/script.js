document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const startBtn = document.getElementById("startBtn");
    const scoreDisplay = document.getElementById("score");
    const messageDisplay = document.getElementById("message");

    const boxSize = 20;
    let snake = [];
    let food = {};
    let score = 0;
    let direction = "";
    let gameInterval;
    let isGameRunning = false;

    // Керування стрілками
    document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft" && direction !== "RIGHT") direction = "LEFT";
        if (event.key === "ArrowUp" && direction !== "DOWN") direction = "UP";
        if (event.key === "ArrowRight" && direction !== "LEFT") direction = "RIGHT";
        if (event.key === "ArrowDown" && direction !== "UP") direction = "DOWN";
    });

    startBtn.addEventListener("click", startGame);

    function startGame() {
        if (isGameRunning) return;
        
        // Скидання налаштувань
        snake = [];
        snake[0] = { x: 9 * boxSize, y: 10 * boxSize };
        score = 0;
        direction = "";
        scoreDisplay.innerText = score;
        messageDisplay.innerText = "";
        isGameRunning = true;
        startBtn.disabled = true;

        spawnFood();
        gameInterval = setInterval(draw, 100);
    }

    function spawnFood() {
        food = {
            x: Math.floor(Math.random() * (canvas.width / boxSize)) * boxSize,
            y: Math.floor(Math.random() * (canvas.height / boxSize)) * boxSize
        };
    }

    function draw() {
        // Очищення екрану
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // === НОВЕ: Малювання обводки (меж) ігрового поля ===
        ctx.strokeStyle = "#d32f2f"; // Колір рамки (червоний, щоб добре було видно)
        ctx.lineWidth = 6;           // Товщина рамки
        // Малюємо прямокутник по краях (відступаємо половину товщини, щоб лінія не обрізалась)
        ctx.strokeRect(3, 3, canvas.width - 6, canvas.height - 6);
        ctx.lineWidth = 1;           // Повертаємо стандартну товщину лінії для змійки
        // ===================================================

        // Малювання змійки
        for (let i = 0; i < snake.length; i++) {
            ctx.fillStyle = (i === 0) ? "#006064" : "#00acc1";
            ctx.fillRect(snake[i].x, snake[i].y, boxSize, boxSize);
            ctx.strokeStyle = "#fff";
            ctx.strokeRect(snake[i].x, snake[i].y, boxSize, boxSize);
        }

        // Малювання їжі
        ctx.fillStyle = "#d32f2f";
        ctx.fillRect(food.x, food.y, boxSize, boxSize);

        // Поточна позиція голови
        let snakeX = snake[0].x;
        let snakeY = snake[0].y;

        // Рух
        if (direction === "LEFT") snakeX -= boxSize;
        if (direction === "UP") snakeY -= boxSize;
        if (direction === "RIGHT") snakeX += boxSize;
        if (direction === "DOWN") snakeY += boxSize;

        // Перевірка на поїдання їжі
        if (snakeX === food.x && snakeY === food.y) {
            score++;
            scoreDisplay.innerText = score;
            spawnFood();
        } else {
            snake.pop(); // Видаляємо хвіст, якщо не з'їли їжу
        }

        let newHead = { x: snakeX, y: snakeY };

        // Перевірка зіткнення зі стінами або самою собою
        // Тут ми враховуємо, що змійка врізається, якщо виходить за межі canvas
        if (snakeX < 0 || snakeX >= canvas.width || snakeY < 0 || snakeY >= canvas.height || collision(newHead, snake)) {
            gameOver();
            return;
        }

        snake.unshift(newHead); // Додаємо нову голову
    }

    function collision(head, array) {
        for (let i = 0; i < array.length; i++) {
            if (head.x === array[i].x && head.y === array[i].y) return true;
        }
        return false;
    }

    function gameOver() {
        clearInterval(gameInterval);
        isGameRunning = false;
        startBtn.disabled = false;
        messageDisplay.innerText = "Гра закінчена! Зберігаємо результат...";
        saveScore();
    }
    function saveScore() {
        const playerName = document.getElementById("playerName").value || "Анонім";
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/booking/save-score/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                player_name: playerName,
                game_name: 'Змійка',
                score: score
            })
        })
        .then(response => response.json())
        .then(data => {
            messageDisplay.innerText = "Результат успішно збережено!";
            messageDisplay.style.color = "green";
        })
        .catch(error => {
            console.error('Помилка:', error);
            messageDisplay.innerText = "Помилка збереження результату.";
        });
    }
});