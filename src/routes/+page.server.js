/** @type {import('./$types').PageServerLoad} */
export async function load({ platform }) {
    const db = platform?.env?.DB;

    if (!db) {
        console.error("SvelteKit cannot find the DB binding object!");
        return { metrics: [] };
    }

    try {
        // Zero filters. If the connection is live, this WILL return 50 rows.
        const { results } = await db
            .prepare(`
                SELECT timestamp, category, value 
                FROM energy_metrics 
                WHERE timestamp >= datetime('now','-10 day') OR category = 'price_cap'
                ORDER BY timestamp ASC 
            `)
            .all();

        console.log(`D1 Connection Success! Retrieved ${results?.length || 0} rows.`);
        
        return {
            metrics: results || []
        };

    } catch (error) {
        console.error("Failed to read from Cloudflare D1:", error);
        return { metrics: [] };
    }
}