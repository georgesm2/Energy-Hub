<script>
    import { Chart } from 'svelte-echarts';
    import { init, use } from 'echarts/core';
    import { LineChart } from 'echarts/charts';
    import { ToolboxComponent, DataZoomComponent, GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';

    // Keep the tree-shaking setup local to the component rendering the chart
    use([LineChart, ToolboxComponent, DataZoomComponent, GridComponent, CanvasRenderer, TooltipComponent, LegendComponent]);

    // Accept only the unified options object via Svelte 5 props
    let { options } = $props();
</script>

<div class="card chart" id="price-chart">
    <h3>Electricity Price £ / kWh</h3>
    <div class="chart-area">
        <Chart {init} {options} />
    </div>
</div>

<style>
    .card {
        background-color: #fff;
        border-radius: 10px;
        min-width: 0;
        box-sizing: border-box;
        text-align: center;
    }
    .chart-area {
        height: 26rem;
        width: 100%;
        overflow: hidden;
    }
    @media (max-width: 610px) {
        .chart-area { height: 25rem; }
    }
</style>