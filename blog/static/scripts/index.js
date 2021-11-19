function searchPosts(route = "/", page = "1") {
  const params = new URLSearchParams();
  params.set("page", page);

  const searchInput = document.getElementById("searchInput");
  if (searchInput && searchInput.value) {
    params.set("query", searchInput.value)
  }

  window.location = `${route}?${params}`;
}

function detectEnterKeyPress(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    searchPosts();
  }
}

function deletePost(postId) {
  if (confirm("Do you really want to delete this post?")) {
    window.location = `/post/${postId}/delete`;
  }
}

function deleteComment(commentId) {
  if (confirm("Do you really want to delete this comment?")) {
    window.location = `/comment/${commentId}/delete`;
  }
}