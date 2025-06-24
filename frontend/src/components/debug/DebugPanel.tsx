// frontend/src/components/debug/DebugPanel.tsx - COMPONENTE TEMPORAL DE DEBUG

import React from 'react';
import { Card } from '../ui/Card';
import { useDeclarationManagement } from '../../hooks/useDeclarationManagement';

const DebugPanel: React.FC = () => {
  const {
    declarations,
    isLoading,
    isRefreshing,
    isCreating,
    error,
    stats
  } = useDeclarationManagement();

  if (process.env.NODE_ENV === 'production') {
    return null; // No mostrar en producción
  }

  return (
    <Card className="fixed bottom-4 right-4 w-80 max-h-96 overflow-auto bg-gray-900 text-white text-xs z-50">
      <div className="p-4">
        <h3 className="text-green-400 font-bold mb-2">🐛 DEBUG PANEL</h3>
        
        <div className="space-y-2">
          <div>
            <span className="text-blue-400">Estados:</span>
            <div className="ml-2">
              <div>isLoading: <span className={isLoading ? 'text-red-400' : 'text-green-400'}>{isLoading.toString()}</span></div>
              <div>isRefreshing: <span className={isRefreshing ? 'text-red-400' : 'text-green-400'}>{isRefreshing.toString()}</span></div>
              <div>isCreating: <span className={isCreating ? 'text-red-400' : 'text-green-400'}>{isCreating.toString()}</span></div>
            </div>
          </div>

          <div>
            <span className="text-blue-400">Declaraciones:</span>
            <div className="ml-2">
              <div>Total: <span className="text-yellow-400">{declarations?.length || 0}</span></div>
              {declarations?.map((d, i) => (
                <div key={i} className="text-xs">
                  {i + 1}. ID: {d.id.substring(0, 12)}... | Año: {d.fiscal_year} | Estado: {d.status}
                </div>
              ))}
            </div>
          </div>

          <div>
            <span className="text-blue-400">Estadísticas:</span>
            <div className="ml-2">
              {stats ? (
                <>
                  <div>Total: {stats.totalDeclarations}</div>
                  <div>Año actual: {stats.hasCurrentYear ? 'Sí' : 'No'}</div>
                  <div>Último año: {stats.lastDeclaration?.fiscal_year || 'N/A'}</div>
                </>
              ) : (
                <div className="text-gray-400">Sin estadísticas</div>
              )}
            </div>
          </div>

          {error && (
            <div>
              <span className="text-red-400">Error:</span>
              <div className="ml-2 text-red-300 break-words">{error}</div>
            </div>
          )}

          <div className="text-gray-400 text-xs mt-2">
            ENV: {import.meta.env.VITE_API_URL || 'default'}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default DebugPanel;