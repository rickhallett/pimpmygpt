window.onload = function () {
  // Initialising the canvas
  var canvas = document.querySelector("canvas"),
    ctx = canvas.getContext("2d");

  // Setting the width and height of the canvas
  canvas.width = window.innerWidth * 0.8;
  canvas.height = window.innerHeight * 0.8;

  // Setting up the letters
  var letters =
    "ABCDEFGHIJKLMﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍHIJKLMNOPQRSTUVXYZABCD012345789TUVXYZABCDEFGHIJKLMNOﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍUVXYZABCDEFGHIJKLMNOPQRSTUVXYZ";
  letters = letters.split("");

  // Setting up the columns
  var fontSize = 10,
    columns = canvas.width / fontSize;

  // columns = 100;

  // Setting up the drops
  var drops = [];
  for (var i = 0; i < columns; i++) {
    drops[i] = parseInt(Math.random() * canvas.height);
  }

  // Setting up the draw function
  function draw() {
    ctx.fillStyle = "rgba(0, 0, 0, .1)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < drops.length; i++) {
      var text = letters[Math.floor(Math.random() * letters.length)];
      ctx.fillStyle = "#0f0";
      ctx.fillText(text, i * fontSize, drops[i] * fontSize);
      drops[i]++;
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.95) {
        drops[i] = 0;
      }
    }
  }

  // Loop the animation
  setInterval(draw, 33);

  const enhancedCategory = document.getElementById(
    "response.enhanced-category"
  )?.value;
  const enhancedSubcategory = document.getElementById(
    "response.enhanced-subcategory"
  )?.value;

  if (document.getElementById("hackers-delight")) {
    document.getElementById("main-category").value = enhancedCategory;
    showSubcategories();
    document.getElementById(`${enhancedCategory}-subcategory`).value =
      enhancedSubcategory;
    showDescription(enhancedCategory);
  }
};

function showSubcategories() {
  var category = document.getElementById("main-category").value;

  [
    "reductive-operations",
    "transformational-operations",
    "generative-operations",
  ].forEach((id) => {
    const name = id.match(/(.*)-operations/)[1];
    const el = document.getElementById(id);
    el.style.display = name === category ? "block" : "none";
    Array.from(el.children[1]).forEach((option) => {
      option.selected = option.value === "";
    });
  });

  document.getElementById("reductive-operations").style.display =
    category === "reductive" ? "block" : "none";

  document.getElementById("transformational-operations").style.display =
    category === "transformational" ? "block" : "none";

  document.getElementById("generative-operations").style.display =
    category === "generative" ? "block" : "none";

  selectedValue = null;

  showDescription(null);
}

function showDescription(category) {
  var descriptions = {
    summarization: "Condenses long content into shorter form.",
    distillation: "Extracts core principles from complex information.",
    extraction: "Pulls out specific data like names or numbers.",
    characterizing: "Identifies the nature or genre of the text.",
    reformatting: "Changes the presentation style of content.",
    refactoring: "Rewrites for better efficiency or clarity.",
    "language-change": "Translates between natural or coding languages.",
    restructuring: "Reorders content for logical flow.",
    modification: "Alters tone, formality, or style.",
    clarification: "Makes content clearer and more articulate.",
    "content-generation":
      "Creating new text based on a given topic or seed phrase.",
    "question-generation":
      "Creating questions based on a given text or context.",
    "code-generation":
      "Writing code snippets or full programs based on user requirements.",
    "dialogue-creation":
      "Generating conversational exchanges between characters or agents.",
    "scenario-building": "Creating hypothetical situations or case studies.",
    "data-simulation":
      "Generating synthetic data sets for testing or analysis.",
    "creative-writing":
      "Generating poems, songs, or other forms of creative text.",
    "instruction-generation": "Creating step-by-step guides or tutorials.",
    prediction: "Making forecasts based on given data or trends.",
    "idea-brainstorming":
      "Generating a list of ideas or solutions for a given problem.",
  };

  var selectedValue = document.getElementById(category + "-subcategory")?.value;
  document.getElementById("subcategory-description").innerText =
    descriptions[selectedValue] || "";

  document.getElementById("last-selected").value = selectedValue;
}
