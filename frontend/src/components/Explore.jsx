import React from 'react';
import ExploreCard from './ExploreCard';

// Updated destination data with verified images
const destinations = [
  {
    city: 'Denver',
    dateRange: 'Sep 2-12',
    imageUrl: 'https://images.unsplash.com/photo-1546156929-a4c0ac411f47?w=800&auto=format&fit=crop'
  },
  {
    city: 'Tokyo',
    dateRange: 'Oct 15-25',
    imageUrl: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&auto=format&fit=crop'
  },
  {
    city: 'Melbourne',
    dateRange: 'Nov 5-15',
    imageUrl: 'https://images.unsplash.com/photo-1545044846-351ba102b6d5?w=800&auto=format&fit=crop'
  },
  {
    city: 'Austin',
    dateRange: 'Sep 20-30',
    imageUrl: 'https://images.unsplash.com/photo-1530089711124-9ca31fb9e863?w=800&auto=format&fit=crop'
  },
  {
    city: 'New York',
    dateRange: 'Dec 1-10',
    imageUrl: 'https://images.unsplash.com/photo-1601933513793-1ac1de44f573?w=800&auto=format&fit=crop'
  },
  {
    city: 'Istanbul',
    dateRange: 'Oct 10-20',
    imageUrl: 'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800&auto=format&fit=crop'
  },
  {
    city: 'Cairo',
    dateRange: 'Nov 22-Dec 2',
    imageUrl: 'https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=800&auto=format&fit=crop'
  },
  {
    city: 'Marrakech',
    dateRange: 'Sep 18-28',
    imageUrl: 'https://images.unsplash.com/photo-1597211684565-dca64d72bdfe?w=800&auto=format&fit=crop'
  }
];

const Explore = () => {
  return (
    <section className="container mx-auto px-6 py-12">
      <h2 className="text-3xl font-bold text-sage-700">Explore</h2>
      <p className="mt-2 text-sage-600">Not sure where to go? Try out some suggestions!</p>

      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {destinations.map((dest) => (
          <ExploreCard
            key={dest.city}
            city={dest.city}
            dateRange={dest.dateRange}
            imageUrl={dest.imageUrl}
          />
        ))}
      </div>
    </section>
  );
};

export default Explore;