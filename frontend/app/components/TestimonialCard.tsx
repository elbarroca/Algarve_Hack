import React from 'react';

interface TestimonialCardProps {
  name: string;
  role: string;
  company: string;
  testimonial: string;
  avatar?: string;
  rating?: number;
}

export const TestimonialCard: React.FC<TestimonialCardProps> = ({
  name,
  role,
  company,
  testimonial,
  avatar,
  rating = 5,
}) => {
  return (
    <div className="group relative p-6 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl hover:border-slate-600 transform hover:scale-105 transition-all duration-500">
      {/* Quote Icon */}
      <div className="absolute top-4 right-4 text-6xl text-blue-500/10 group-hover:text-blue-500/20 transition-colors duration-500">
        "
      </div>

      {/* Rating */}
      <div className="flex gap-1 mb-4">
        {[...Array(rating)].map((_, index) => (
          <span key={index} className="text-yellow-400 text-lg">
            ★
          </span>
        ))}
      </div>

      {/* Testimonial Text */}
      <p className="text-slate-300 leading-relaxed mb-6 relative z-10">
        "{testimonial}"
      </p>

      {/* Author Info */}
      <div className="flex items-center gap-4">
        {avatar ? (
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 overflow-hidden">
            <img src={avatar} alt={name} className="w-full h-full object-cover" />
          </div>
        ) : (
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
            {name.charAt(0)}
          </div>
        )}
        <div>
          <h4 className="text-white font-semibold">{name}</h4>
          <p className="text-slate-400 text-sm">
            {role} @ {company}
          </p>
        </div>
      </div>
    </div>
  );
};

