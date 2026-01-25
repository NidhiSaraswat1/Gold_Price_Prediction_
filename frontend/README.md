# Gold Price Prediction Frontend

A modern Next.js frontend for the Gold Price Prediction API deployed on Hugging Face Spaces.

## Features

- 🎨 Beautiful, modern UI with gradient designs
- 📱 Fully responsive design
- ⚡ Fast and efficient API integration
- 🔮 Real-time gold price predictions
- 📊 Visual representation of price changes and market direction

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

### Development

Run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### Build for Production

```bash
npm run build
npm start
# or
yarn build
yarn start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx      # Root layout component
│   ├── page.tsx        # Main prediction page
│   └── globals.css     # Global styles
├── lib/
│   └── api.ts          # API integration service
├── public/             # Static assets
├── package.json        # Dependencies
├── tsconfig.json      # TypeScript configuration
├── tailwind.config.js # Tailwind CSS configuration
└── next.config.js     # Next.js configuration
```

## API Integration

The frontend connects to the Hugging Face Spaces API at:
`https://nidhisarai-gold-price-prediction.hf.space/api/predict`

The API endpoint accepts POST requests and returns:
- `current_price`: Current gold price
- `predicted_price`: Predicted price for tomorrow
- `price_change`: Expected change in price
- `direction`: Market direction (BULLISH/BEARISH)
- `status`: Request status

## Technologies Used

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Hooks**: State management

## License

MIT

