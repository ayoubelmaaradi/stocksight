import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';
import io from 'socket.io-client';


@Injectable({
  providedIn: 'root'
})
export class SocketClientService {
  chart: any;
  doughnut: any;
  socket = io(environment.socketUrl);
  constructor() {
  }

  init() {
    this.socket.on('data1', (res) => {
      this.updateChartData(this.chart, res, 0);
      this.updateChartData(this.doughnut, res.slice(0, 5), 0);
    })

    this.socket.on('data2', (res) => {
      this.updateChartData(this.chart, res, 1);
    })
  }

  updateChartData(chartdata, res, num) {
  }
}
