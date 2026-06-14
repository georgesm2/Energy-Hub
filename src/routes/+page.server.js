/** @type {import('./$types').PageServerLoad} */
export async function load({ platform }) {
    const db = platform?.env?.energy_db;

    if (!db) {
        console.error("Database binding missing!")
        return { metrics: []};
    }

    try {
        const {results} = await db.prepare(`
            SELECT timestamp, category, value
            FROM energy_metrics
            WHERE timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp DESC
            `)
        .all();

        return {
            metrics: results
        };
    } catch (error) {
        console.error("Failed to read from D1: ", error);
        return { metrics: []};
    }
}