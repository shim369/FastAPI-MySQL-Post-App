document
  .getElementById("addPostForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const jsonData = {};
    formData.forEach((value, key) => {
      jsonData[key] = value;
    });

    try {
      const response = await fetch("/posts/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
      });
      if (!response.ok) {
        throw new Error("Failed to add post");
      }
      window.location.href = "/";
    } catch (error) {
      console.error("Error:", error);
    }
  });
