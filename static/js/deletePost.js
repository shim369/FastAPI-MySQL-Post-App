async function deletePost(postId) {
  try {
    const response = await fetch(`/posts/${postId}`, {
      method: "DELETE",
    });
    if (response.ok) {
      location.reload();
    } else {
      console.error("Failed to delete post");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}
