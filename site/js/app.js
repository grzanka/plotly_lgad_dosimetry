import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

var APP = {

	Player: function () {

		var renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.outputEncoding = THREE.sRGBEncoding;

		var labelRenderer;
		
		var loader = new THREE.ObjectLoader();
		var camera, scene;

		var events = {};

		var dom = document.createElement('div');
		dom.appendChild(renderer.domElement);

		this.dom = dom;

		this.width = 800;
		this.height = 800;

		this.load = function (json) {

			this.setScene(loader.parse(json.scene));

			const axesHelper = new THREE.AxesHelper( 1 );
			axesHelper.layers.enableAll();
			scene.add( axesHelper );
			this.setCamera(loader.parse(json.camera));

			labelRenderer = new CSS2DRenderer();
			labelRenderer.setSize( window.innerWidth, window.innerHeight );
			labelRenderer.domElement.style.position = 'absolute';
			labelRenderer.domElement.style.top = '0px';
			document.body.appendChild( labelRenderer.domElement );

			for(let i = 0; i < scene.children.length; i++) {
				const object = scene.children[i];
				if (object.type == 'Mesh') {						
					const objectDiv = document.createElement( 'div' );
					objectDiv.className = 'label';
					objectDiv.textContent = object.name;
					objectDiv.style.marginTop = 'em';
					const objectLabel = new CSS2DObject( objectDiv );
					objectLabel.position.set( 0, 0, 0 );
					if(object.name == 'E1'){
						objectLabel.position.set( 0, 0.0, 0.3 );
					}
					if(object.name !== 'beam axis' & object.name !== 'Beam'){
						object.add( objectLabel);
					}
					objectLabel.layers.set( 0 );
				}
			}

			const controls = new OrbitControls( camera, labelRenderer.domElement );
			
			events = {
				init: [],
				start: [],
				stop: [],
				update: []
			};
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

		function animate() {
			// const time = - performance.now() * 0.0003;
			// camera.position.x = 12 * Math.cos( time );
			// camera.position.y = 2 * Math.cos( 0.3*time );
			// camera.position.z = 12 * Math.sin( time );
			// camera.lookAt( scene.position );
			renderer.render(scene, camera);
			labelRenderer.render( scene, camera );
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
			dispatch(events.update, { time: time * 1000, delta: 1 });
			renderer.render(scene, camera);
			labelRenderer.render( scene, camera );
		};

		this.dispose = function () {
			renderer.dispose();
			labelRenderer.dispose();
			camera = undefined;
			scene = undefined;
		};

	}

};

export { APP };
