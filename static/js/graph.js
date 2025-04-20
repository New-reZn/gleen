function initChart(){

  const canvas = document.getElementById('chart');
  const container = canvas.parentElement;

  if (!canvas) return;
    
  if (window.activeChart) {
      window.activeChart.destroy();
  }

  canvas.width = container.offsetWidth;
  canvas.height = container.offsetWidth * (1/3.2);

  const ctx = canvas.getContext('2d');

  const labels = JSON.parse(document.getElementById('labels-data').textContent);
  const dataset = JSON.parse(document.getElementById('dataset-data').textContent);

  const datasets=[]
  const datasetKeys=Object.keys(dataset);

  for ( let dataset_name of datasetKeys){
    datasets.push(
      {
          label: dataset_name,
          data: dataset[dataset_name],
          borderWidth: 2,
          tension: 0.1
      }
    )
  }

  window.activeChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets
    },
    options: {
      responsive: false,
      maintainAspectRatio: false,
      
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            color: 'rgba(204 , 204, 204, .6)',
          },
          ticks: {
            color: '#ccc',
            font: {
              size: 12
            },
          },
          border: {
            dash: [4, 6],
            display: true
          } 
        },
        y: {
          beginAtZero: true,
          grid: {
            color: function(context) {
              return context.tick.value === 0 ? 'rgba(204, 204, 204, .6)' : 'rgba(0, 0, 0, 0)';
            },
          },
          ticks: {
            color: '#ccc',
            font: {
              size: 12
            },
            callback: function(value) {
              if (value % 1 === 0) {
                return value;
              }
            },
            stepSize: 1,
          },
        }
      }
    }
  });

};

document.addEventListener('DOMContentLoaded', initChart);
document.body.addEventListener('htmx:afterSwap', function(evt) {
  if (evt.detail.target.id === 'graph-component') {
    initChart();
  }
});

new ResizeObserver(entries => {
  initChart();
}).observe(document.querySelector('#chart-container'));

window.addEventListener('beforeunload', () => {
  if (window.activeChart) {
    window.activeChart.destroy();
  }
});