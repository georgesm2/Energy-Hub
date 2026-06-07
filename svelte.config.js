import adapter from '@sveltejs/adapter-static';

const dev = process.argv.includes('dev');

export default {
	kit: {
		adapter: adapter({ fallback: '404.html' }),
		paths: {
			base: dev ? '' : '/Energy-Hub'
		}
	}
};