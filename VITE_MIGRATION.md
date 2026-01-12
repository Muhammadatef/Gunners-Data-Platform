# Vite React Frontend - Replace Next.js

Update docker-compose.yml to use frontend-vite instead of frontend:

```yaml
  # Frontend - Vite React App (Lighter & Faster)
  frontend:
    build:
      context: ./frontend-vite
      dockerfile: Dockerfile
    container_name: arsenalfc_frontend
    environment:
      VITE_GRAPHQL_URL: http://backend:4000/graphql
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: always
    networks:
      - arsenalfc_network
```

## Benefits of Vite:
- ✅ Build time: 10-30 seconds (vs 45+ minutes)
- ✅ No SSR complications
- ✅ Hot Module Replacement (instant updates)
- ✅ Smaller bundle size
- ✅ Simpler architecture
- ✅ Same modern UI capabilities

## Next Steps:
1. Let npm install complete
2. Copy all dashboard components
3. Build and test locally (takes seconds!)
4. Once working, update docker-compose
5. Deploy
