const chat = document.getElementById("chat");
const questionInput = document.getElementById("question");
const sendButton = document.getElementById("sendButton");
const loading = document.getElementById("loading");


function addMessage(message, type) {

    const messageDiv = document.createElement("div");

    messageDiv.className = `message ${type}`;

    const avatar = document.createElement("div");

    avatar.className = "avatar";

    avatar.textContent = type === "user" ? "You" : "AI";


    const bubble = document.createElement("div");

    bubble.className = "bubble";


    const text = document.createElement("p");

    text.textContent = message;


    bubble.appendChild(text);

    messageDiv.appendChild(avatar);

    messageDiv.appendChild(bubble);

    chat.appendChild(messageDiv);


    chat.scrollTop = chat.scrollHeight;
}


async function askQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }


    // Show user's message

    addMessage(question, "user");


    // Clear input

    questionInput.value = "";

    questionInput.style.height = "auto";


    // Disable button

    sendButton.disabled = true;

    loading.classList.remove("hidden");


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );

        }


        addMessage(
            data.answer || "No answer was returned.",
            "assistant"
        );


    } catch (error) {

        addMessage(
            "Sorry, I couldn't process your question. Please try again.",
            "assistant"
        );

        console.error(error);

    } finally {

        loading.classList.add("hidden");

        sendButton.disabled = false;

        questionInput.focus();

    }
}


/* =========================
   SEND BUTTON
========================= */

sendButton.addEventListener(
    "click",
    askQuestion
);


/* =========================
   ENTER TO SEND
========================= */

questionInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askQuestion();

        }

    }
);


/* =========================
   AUTO RESIZE
========================= */

questionInput.addEventListener(
    "input",
    function() {

        this.style.height = "auto";

        this.style.height =
            Math.min(this.scrollHeight, 130) + "px";

    }
);
