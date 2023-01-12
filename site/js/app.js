import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

var APP = {

	Player: function () {

		var renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setPixelRatio(window.devicePixelRatio); // TODO: Use player.setPixelRatio()
		renderer.outputEncoding = THREE.sRGBEncoding;

		var loader = new THREE.ObjectLoader();
		var camera, scene;

		var events = {};

		var dom = document.createElement('div');
		dom.appendChild(renderer.domElement);

		this.dom = dom;

		this.width = 800;
		this.height = 800;

		this.load = function (json) {

			var project = json.project;

			this.setScene(loader.parse(json.scene));
			this.setCamera(loader.parse(json.camera));

			const controls = new OrbitControls(camera, renderer.domElement);

			events = {
				init: [],
				start: [],
				stop: [],
				update: []
			};

			var scriptWrapParams = 'player,renderer,scene,camera';
			var scriptWrapResultObj = {};

			for (var eventKey in events) {

				scriptWrapParams += ',' + eventKey;
				scriptWrapResultObj[eventKey] = eventKey;

			}

			var scriptWrapResult = JSON.stringify(scriptWrapResultObj).replace(/\"/g, '');

			for (var uuid in json.scripts) {

				var object = scene.getObjectByProperty('uuid', uuid, true);

				if (object === undefined) {

					console.warn('APP.Player: Script without object.', uuid);
					continue;

				}

				var scripts = json.scripts[uuid];

				for (var i = 0; i < scripts.length; i++) {

					var script = scripts[i];

					var functions = (new Function(scriptWrapParams, script.source + '\nreturn ' + scriptWrapResult + ';').bind(object))(this, renderer, scene, camera);

					for (var name in functions) {

						if (functions[name] === undefined) continue;

						if (events[name] === undefined) {

							console.warn('APP.Player: Event type not supported (', name, ')');
							continue;

						}

						events[name].push(functions[name].bind(object));

					}

				}

			}

			dispatch(events.init, arguments);

		};

		this.setCamera = function (value) {

			camera = value;
			camera.aspect = this.width / this.height;
			camera.updateProjectionMatrix();

		};

		this.setScene = function (value) {
			scene = value;
		};

		this.setPixelRatio = function (pixelRatio) {
			renderer.setPixelRatio(pixelRatio);
		};

		this.setSize = function (width, height) {

			this.width = width;
			this.height = height;

			if (camera) {
				camera.aspect = this.width / this.height;
				camera.updateProjectionMatrix();
			}
			renderer.setSize(width, height);

		};

		function dispatch(array, event) {

			for (var i = 0, l = array.length; i < l; i++) {
				array[i](event);
			}

		}

		var time, startTime, prevTime;

		function animate() {

			time = performance.now();
			try {
				dispatch(events.update, { time: time - startTime, delta: time - prevTime });
			} catch (e) {
				console.error((e.message || e), (e.stack || ''));
			}
			renderer.render(scene, camera);
			prevTime = time;
		}

		this.play = function () {

			dispatch(events.start, arguments);
			renderer.setAnimationLoop(animate);

		};

		this.stop = function () {
			dispatch(events.stop, arguments);
			renderer.setAnimationLoop(null);

		};

		this.render = function (time) {

			dispatch(events.update, { time: time * 1000, delta: 0 /* TODO */ });
			renderer.render(scene, camera);

		};

		this.dispose = function () {

			renderer.dispose();

			camera = undefined;
			scene = undefined;

		};

	}

};

export { APP };
