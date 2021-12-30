$(function(e){
  'use strict'

	/*-----echartArea2-----*/
  var areaData2 = [
    {
      name: 'Sales',
      type: 'line',
      smooth: true,
      data: [12, 65, 33, 45, 45, 78, 19],
	  symbolSize:20,
	   lineStyle: {
			normal: { width: 4 ,

			}
		},

    },
    {
      name: 'Orders',
      type: 'line',
      smooth: true,
      data: [4, 23, 55, 76, 77, 68, 99],
      symbolSize:20,
	   lineStyle: {
			normal: { width: 4 ,

			}
		},
    }
  ];

  var optionArea2 = {
    grid: {
      top: '6',
      right: '12',
      bottom: '17',
      left: '25',
    },
    xAxis: {
      data: [ '2013', '2014', '2015', '2016', '2017', '2018'],
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: '#e9ecf3' }
      },
      axisLabel: {
        fontSize: 10,
        color: '#a7acbf',
		display:'false'
      },
    },
	tooltip: {
		show: true,
		showContent: true,
		alwaysShowContent: true,
		triggerOn: 'mousemove',
		trigger: 'axis',
		axisPointer:
			{
				label: {
					show: false,
				}
			}

	},
    yAxis: {
      splitLine: {
        lineStyle: { color: '#e9ecf3' },
		display:false
      },
      axisLine: {
        lineStyle: { color: '#e9ecf3' },
		display:false
      },
      axisLabel: {
        fontSize: 10,
        color: '#a7acbf'
      }
    },
    series: areaData2,
    color:[ '#ff4d83','#4d83ff']
  };

  var chartArea2 = document.getElementById('echartArea2');
  var areaChart2 = echarts.init(chartArea2);
  areaChart2.setOption(optionArea2);




});

//morris chart
$(function(e){
  'use strict'

	new Morris.Donut({
		  element: 'morrisBar8',
		  data: [
			{value: 15, label: 'Product A'},
			{value: 30, label: 'Product B'},
			{value: 45, label: 'Product C'},
			{value: 20, label: 'Product D'},
		  ],
		  colors: [
		'#4dffc9', '#4d83ff', '#ff4d83', '#ffc94d'

	  ],
		  formatter: function (x) { return x + "%"}
		}).on('click', function(i, row){
		  console.log(i, row);
	});
});

