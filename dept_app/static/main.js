console.log("main.js 已加载");

$(document).ready(function () {
  $("#my-button").click(function () {
    $.ajax({
      url: "http://127.0.0.1:8000/api/haha",
      method: "GET",
      success: function (data) {
        console.log("请求成功: ", data);
        $("#my-result").html(data.message);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log("请求失败: ", textStatus, errorThrown);
        $("#my-result").html("请求失败");
      },
    });
  });
});
