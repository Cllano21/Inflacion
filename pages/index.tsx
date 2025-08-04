import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function Home() {
  const [data, setData] = useState<any[]>([]);
  const [anual, setAnual] = useState<number>(0);
  const [fecha, setFecha] = useState<string>("");

  useEffect(() => {
    fetch("/datos.json")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        const ultimo = json[json.length - 1];
        setAnual(ultimo.anual);
        setFecha(ultimo.Mes);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-300 via-blue-800 to-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-6">Inflación en Ecuador</h1>

      <div className="flex gap-4 mb-6">
        <div className="bg-white bg-opacity-10 backdrop-blur rounded-xl p-4 w-48 text-center">
          <h2 className="text-sm mb-1">Índice General</h2>
          <p className="text-xs text-gray-200">{fecha}</p>
          <p className="text-xl font-semibold text-yellow-300">
            {data.length > 0 ? data[data.length - 1].IPC.toFixed(2) : "--"}
          </p>
        </div>
        <div className="bg-white bg-opacity-10 backdrop-blur rounded-xl p-4 w-52 text-center">
          <h2 className="text-sm mb-1">Inflación Anual</h2>
          <p className="text-xs text-gray-200">{fecha}</p>
          <p className="text-xl font-semibold text-sky-400">
            {(anual * 100).toFixed(2)}%
          </p>
        </div>
      </div>

      <div className="bg-white bg-opacity-10 backdrop-blur rounded-xl p-4">
        <Plot
          data={[
            {
              x: data.map((d) => d.Mes),
              y: data.map((d) => d.IPC),
              type: "scatter",
              mode: "lines+markers",
              name: "IPC General",
              line: { color: "#FFDE21" },
            },
            {
              x: data.map((d) => d.Mes),
              y: data.map((d) => d.anual * 100),
              type: "scatter",
              mode: "lines+markers",
              name: "Variación Anual",
              line: { color: "#FFDE21", dash: "dash" },
              yaxis: "y2",
            },
          ]}
          layout={{
            height: 350,
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { color: "white" },
            title: {
              text: "IPC y Variación Anual",
              font: { color: "white" },
              pad: { b: 0 },
            },
            xaxis: { title: "Fecha", color: "white" },
            yaxis: { title: "IPC", titlefont: { color: "white" }, tickfont: { color: "white" } },
            yaxis2: {
              overlaying: "y",
              side: "right",
              title: "Variación Anual (%)",
              titlefont: { color: "white" },
              tickfont: { color: "white" },
            },
            legend: {
              orientation: "h",
              x: 0,
              y: 1.1,
              font: { color: "white" },
            },
          }}
        />
      </div>
    </main>
  );
}
