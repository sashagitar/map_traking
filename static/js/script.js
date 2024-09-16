var selectedPointId = null;

function init() {
  var map = new ymaps.Map("map", {
    center: [55.76, 37.64], // Временные координаты центра карты
    zoom: 10, // Временный зум карты
  });

  var routePoints = [];
  var startPoint = null;
  var endPoint = null;

  // Добавление точек маршрута и сбор координат для линии
  routePointsData.forEach(function (point) {
    var pointType = point.point_type;
    var pointCoords = [point.latitude, point.longitude];
    var pointId = point.id;
    routePoints.push(pointCoords);
    var pointPlacemark = new ymaps.Placemark(
      pointCoords,
      {
        balloonContent: pointType,
      },
      {
        preset:
          pointType === "start"
            ? "islands#greenDotIcon"
            : pointType === "end"
            ? "islands#redDotIcon"
            : "islands#blueDotIcon",
      }
    );
    map.geoObjects.add(pointPlacemark);

    // Обработчик клика по метке для редактирования точки
    pointPlacemark.events.add("click", function () {
      document.getElementById("latitude").value = pointCoords[0];
      document.getElementById("longitude").value = pointCoords[1];
      document.getElementById("point_id").value = pointId;
      document.getElementById("submit_button").innerText = "Изменить точку";
      document.getElementById("cancel_button").style.display = "inline";
      selectedPointId = pointId;
    });

    // Устанавливаем начальную и конечную точки
    if (pointType === "start") {
      startPoint = pointCoords;
    }
    if (pointType === "end") {
      endPoint = pointCoords;
    }
  });

  // Создание линии маршрута
  function drawRoute() {
    if (routePoints.length > 1) {
      var polyline = new ymaps.Polyline(
        routePoints,
        {
          balloonContent: "Маршрут",
        },
        {
          strokeColor: "#0000FF",
          strokeWidth: 4,
          strokeOpacity: 0.6,
        }
      );
      map.geoObjects.add(polyline);

      // Установка границ карты, чтобы все точки маршрута были видны
      map.setBounds(polyline.geometry.getBounds(), {
        checkZoomRange: true,
      });
    } else if (routePoints.length === 1) {
      // Если есть только одна точка, центрируем и зумируем на ней
      map.setCenter(routePoints[0], 14);
    }
  }

  drawRoute();

  // Добавление новой точки или изменение координат существующей точки по клику на карту
  map.events.add("click", function (e) {
    var coords = e.get("coords");
    var pointType = document.getElementById("point_type").value;

    document.getElementById("latitude").value = coords[0];
    document.getElementById("longitude").value = coords[1];

    if (selectedPointId) {
      document.getElementById("submit_button").innerText = "Изменить точку";
    } else {
      document.getElementById("point_id").value = "";
      if (pointType === "start") {
        document.getElementById("submit_button").innerText =
          "Добавить начало маршрута";
      } else if (pointType === "end") {
        document.getElementById("submit_button").innerText =
          "Добавить конец маршрута";
      } else {
        document.getElementById("submit_button").innerText = "Добавить точку";
      }
      document.getElementById("cancel_button").style.display = "none";
    }

    // Добавление серой метки
    var tempPlacemark = new ymaps.Placemark(
      coords,
      {},
      {
        preset: "islands#grayDotIcon",
      }
    );
    map.geoObjects.add(tempPlacemark);

    // Удаление предыдущей серой метки, если она существует
    if (window.tempPlacemark) {
      map.geoObjects.remove(window.tempPlacemark);
    }
    window.tempPlacemark = tempPlacemark;
  });

  // Обновление координат для начальной и конечной точки
  if (startPoint) {
    document.getElementById("start_latitude").value = startPoint[0];
    document.getElementById("start_longitude").value = startPoint[1];
    document.getElementById("submit_button").innerText =
      "Изменить начало маршрута";
  }
  if (endPoint) {
    document.getElementById("end_latitude").value = endPoint[0];
    document.getElementById("end_longitude").value = endPoint[1];
    document.getElementById("submit_button").innerText =
      "Изменить конец маршрута";
  }
}

function updateForm() {
  var pointType = document.getElementById("point_type").value;
  var submitButton = document.getElementById("submit_button");

  if (selectedPointId) {
    submitButton.innerText = "Изменить точку";
  } else if (pointType === "start") {
    submitButton.innerText = "Добавить начало маршрута";
  } else if (pointType === "end") {
    submitButton.innerText = "Добавить конец маршрута";
  } else {
    submitButton.innerText = "Добавить точку";
  }
}

function cancelEdit() {
  selectedPointId = null;
  document.getElementById("point_id").value = "";
  document.getElementById("latitude").value = "";
  document.getElementById("longitude").value = "";
  var pointType = document.getElementById("point_type").value;

  if (pointType === "start") {
    document.getElementById("submit_button").innerText =
      "Добавить начало маршрута";
  } else if (pointType === "end") {
    document.getElementById("submit_button").innerText =
      "Добавить конец маршрута";
  } else {
    document.getElementById("submit_button").innerText = "Добавить точку";
  }
  document.getElementById("cancel_button").style.display = "none";
}

ymaps.ready(init);
