<script>
    // 🧠 SvelteKit automatically populates this property with the load() return payload
    let { data } = $props(); 
</script>

<main class="dashboard-container">
    <h1>UK Energy Hub Metrics</h1>
    <p>Displaying the latest {data.metrics.length} data points extracted from Cloudflare D1.</p>

    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Timestamp (UTC)</th>
                    <th>Category Stream</th>
                    <th>Recorded Value</th>
                </tr>
            </thead>
            <tbody>
                {#each data.metrics as metric}
                    <tr>
                        <td>{metric.timestamp}</td>
                        <td class="badge">{metric.category}</td>
                        <td>{metric.value.toFixed(4)}</td>
                    </tr>
                {:else}
                    <tr>
                        <td colspan="3">No historical data streamed yet.</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</main>

<style>
    .dashboard-container { padding: 2rem; font-family: sans-serif; }
    .table-wrapper { margin-top: 1.5rem; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th, td { padding: 0.75rem; border-bottom: 1px solid #ddd; }
    th { background-color: #f4f4f4; }
    .badge { font-weight: bold; color: #2563eb; }
</style>