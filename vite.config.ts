import { sveltekit } from '@sveltejs/kit/vite';
import { cloudflare } from "@cloudflare/vite-plugin";
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit(), cloudflare()]
});