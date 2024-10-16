import React from 'react';
import { Card, CardContent, Table, TableContainer } from '@mui/material';

function PortfolioDashboard() {

  return (
    <Card style={{ marginTop: '20px' }}>
      <CardContent>
        <TableContainer>
          <Table>
            <div>    
            <iframe src="https://e2-demo-field-eng.cloud.databricks.com/embed/dashboardsv3/01ef7368d19618fab70c5a0750da9a95?o=1444828305810485" width="100%" height="600" frameborder="0"></iframe>
            </div>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}

export default PortfolioDashboard;